"""
Layered application logging.

Usage:
    from backend.app.common.logging import LayerLogger

    logger = LayerLogger("infrastructure", "database").get()
    logger = LayerLogger("application", "auth").get()

Console output is human-readable.
File output is a valid JSON array at:
    backend/app/logging/logs/{layer}_logs.json

Each layer writes to its own file so infrastructure noise doesn't
drown out application-level events.
"""

import logging
import os
import sys

from pythonjsonlogger import json as jsonlogger

# backend/app/logging/logs/
_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOGS_DIR = os.path.join(_APP_DIR, "logging", "logs")

LAYERS = frozenset({"api", "application", "domain", "infrastructure"})


class _JsonArrayFileHandler(logging.FileHandler):
    """
    File handler that maintains a valid JSON array log file.

    The file is always parseable with json.load() — even across restarts.
    On open: if a previous session left a closed array, the trailing ] is
    stripped so new entries can be appended.
    On close: the array is properly terminated with ].
    """

    def __init__(self, filename: str, level: int = logging.NOTSET):
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Resume an existing array from a prior session
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, "r+") as f:
                content = f.read().rstrip()
                if content.endswith("]"):
                    # Strip the closing bracket so we can append
                    f.seek(0)
                    f.truncate()
                    f.write(content[:-1].rstrip())

        super().__init__(filename, mode="a", delay=False)
        self.setLevel(level)
        self._first = os.path.getsize(filename) == 0

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            with self.lock:
                if self._first:
                    self.stream.write("[\n" + msg)
                    self._first = False
                else:
                    self.stream.write(",\n" + msg)
                self.flush()
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        try:
            with self.lock:
                if not self._first:
                    self.stream.write("\n]")
                    self.flush()
        except Exception:
            pass
        super().close()


class LayerLogger:
    """
    A named logger scoped to an architectural layer.

    Args:
        layer:         one of "api", "application", "domain", "infrastructure"
        name:          component name within the layer (e.g. "database", "auth")
        console_level: minimum level for stdout output (default DEBUG)
        file_level:    minimum level written to the JSON file (default INFO)

    The resulting logger name is "{layer}.{name}", so log records are naturally
    filterable and hierarchical (e.g. "infrastructure.database").
    """

    def __init__(
        self,
        layer: str,
        name: str,
        console_level: int = logging.DEBUG,
        file_level: int = logging.INFO,
    ):
        if layer not in LAYERS:
            raise ValueError(
                f"Invalid layer '{layer}'. Must be one of: {', '.join(sorted(LAYERS))}"
            )

        logger_name = f"{layer}.{name}"
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.DEBUG)

        if not self._logger.handlers:
            # Console — human-readable with layer context
            console = logging.StreamHandler(sys.stdout)
            console.setLevel(console_level)
            console.setFormatter(logging.Formatter(
                "%(asctime)s [%(name)-32s] %(levelname)-8s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            ))
            self._logger.addHandler(console)

            # File — valid JSON array, one object per entry
            log_file = os.path.join(_LOGS_DIR, f"{layer}_logs.json")
            file_handler = _JsonArrayFileHandler(log_file, level=file_level)
            file_handler.setFormatter(jsonlogger.JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            ))
            self._logger.addHandler(file_handler)

    def get(self) -> logging.Logger:
        return self._logger
