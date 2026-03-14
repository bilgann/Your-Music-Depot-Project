import logging
import os

from pythonjsonlogger import json
import sys


class DBLogger:
    """
    Database Logger Configuration

    Supports dual logging:
    - Console: human-readable for developers
    - File: JSON for auditing / machine-readable
    """
    json_file = os.path.join(os.path.dirname(__file__), "logs", "db_logs.json")
    def __init__(self, name: str = "db_logger", console_level=logging.DEBUG, file_level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # capture all levels, let handlers filter

        # Prevent duplicate handlers if logger already configured
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(console_level)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

            # File handler (JSON)
            os.makedirs(os.path.dirname(self.json_file), exist_ok=True)
            file_handler = logging.FileHandler(self.json_file)
            file_handler.setLevel(file_level)
            json_formatter = json.JsonFormatter(
                '%(asctime)s %(name)s %(levelname)s %(message)s'
            )
            file_handler.setFormatter(json_formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger