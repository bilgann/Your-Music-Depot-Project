import datetime
import logging
import threading
from typing import Optional

import jwt

from backend.app.infrastructure.models import User

_INACTIVITY_LIMIT = datetime.timedelta(minutes=30)


class Auth:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, secret_key: Optional[str] = None, logger: Optional[logging.Logger] = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._secret_key = secret_key or "supersecretkey"
                    cls._instance._algorithm = "HS256"
                    cls._instance._blacklist: set = set()
                    cls._instance._last_active: dict = {}   # token → last-seen datetime
                    cls._instance._logger = logger
        return cls._instance

    # ── Authentication ────────────────────────────────────────────────────────

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Validate credentials and issue a signed JWT containing the user's role."""
        user = User.validate_user(username, password)
        if user:
            payload = {
                "user_id": user.id,
                "username": user.username,
                "role": user.role,
                "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
            }
            token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
            if self._logger:
                self._logger.info(f"User '{username}' authenticated, token issued.")
            return token
        if self._logger:
            self._logger.warning(f"Failed login attempt for username '{username}'.")
        return None

    # ── Token management ──────────────────────────────────────────────────────

    def drop_token(self, token: str) -> bool:
        """Blacklist a token on logout and remove its inactivity record."""
        self._blacklist.add(token)
        self._last_active.pop(token, None)
        if self._logger:
            self._logger.info("Token blacklisted (logout).")
        return True

    def get_user(self, token: str) -> Optional[User]:
        """
        Decode and validate a JWT.
        Returns None if the token is blacklisted, expired, inactive for >30 min,
        or otherwise invalid.
        """
        if token in self._blacklist:
            return None

        # NFR-10: 30-minute inactivity timeout
        last = self._last_active.get(token)
        if last is not None:
            idle = datetime.datetime.now(datetime.timezone.utc) - last
            if idle > _INACTIVITY_LIMIT:
                self._blacklist.add(token)
                self._last_active.pop(token, None)
                if self._logger:
                    self._logger.info("Token expired due to inactivity.")
                return None

        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            # Refresh inactivity clock on every valid use
            self._last_active[token] = datetime.datetime.now(datetime.timezone.utc)
            return User(payload["user_id"], payload["username"], role=payload.get("role", "admin"))
        except jwt.ExpiredSignatureError:
            if self._logger:
                self._logger.warning("Token expired.")
        except jwt.InvalidTokenError:
            if self._logger:
                self._logger.warning("Invalid token.")
        return None
