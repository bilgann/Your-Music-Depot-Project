import datetime
import logging
import threading
from typing import Optional

import jwt

from backend.app.models.user import User


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
                    cls._instance._blacklist = set()  # For logout
                    cls._instance._logger = logger
        return cls._instance

    def authenticate(self, username: str, password: str) -> Optional[str]:
        user = User.validate_user(username, password)
        if user:
            payload = {
                "user_id": user.id,
                "username": user.username,
                "exp": datetime.datetime.now() + datetime.timedelta(hours=1)
            }
            token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
            if self._logger:
                self._logger.info(f"User '{username}' authenticated, token issued.")
            return token
        if self._logger:
            self._logger.warning(f"Failed login attempt for username '{username}'.")
        return None

    def drop_token(self, token: str) -> bool:
        self._blacklist.add(token)
        if self._logger:
            self._logger.info("Token blacklisted (logout).")
        return True

    def get_user(self, token: str) -> Optional[User]:
        if token in self._blacklist:
            if self._logger:
                self._logger.info("Token is blacklisted.")
            return None
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return User(payload["user_id"], payload["username"])
        except jwt.ExpiredSignatureError:
            if self._logger:
                self._logger.warning("Token expired.")
        except jwt.InvalidTokenError:
            if self._logger:
                self._logger.warning("Invalid token.")
        return None