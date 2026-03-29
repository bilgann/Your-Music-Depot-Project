import os
from threading import Lock
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client

from backend.app.common.logging import LayerLogger


class DatabaseConnection:
    """
    Singleton Supabase client.

    Lazily initializes the client, validates environment variables,
    and performs a connectivity health-check on first instantiation.
    """

    _env_location = "../../.env"
    _envar_url_name = "SUPABASE_URL"
    _envar_key_name = "SUPABASE_KEY"

    _lock = Lock()
    _instance = None

    client: Optional[Client] = None

    def __new__(cls, env_location: Optional[str] = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    if env_location:
                        cls._instance._env_location = env_location
                    cls._instance._logger = LayerLogger("infrastructure", "database").get()
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        load_dotenv(os.path.join(os.path.dirname(__file__), self._env_location))

        self._envar_url = os.getenv(self._envar_url_name)
        self._envar_key = os.getenv(self._envar_key_name)
        self._validate_envars()

        self.client: Client = create_client(self._envar_url, self._envar_key)
        self._validate_connection()

    def _validate_envars(self):
        if not self._envar_url:
            self._logger.error(f"{self._envar_url_name} is missing in environment.")
            raise ValueError(f"{self._envar_url_name} must be set in environment variables.")
        if not self._envar_key:
            self._logger.error(f"{self._envar_key_name} is missing in environment.")
            raise ValueError(f"{self._envar_key_name} must be set in environment variables.")

    def _validate_connection(self):
        """
        Flexible health check: tries to list tables, then fallback to select from 'lesson' table.
        Raises ConnectionError if Supabase cannot be reached.
        """
        try:
            self.client.rpc("pg_tables").execute()
        except Exception:
            try:
                self.client.table("lesson").select("lesson_id").limit(1).execute()
            except Exception as e:
                self._logger.error(f"Supabase connection failed: {e}")
                raise ConnectionError(f"Failed to connect to Supabase: {e}")

    def __repr__(self):
        return f"<DatabaseConnection client_initialized={self.client is not None}>"
