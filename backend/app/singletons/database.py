import os
from supabase import create_client, Client
from dotenv import load_dotenv
from threading import Lock
from typing import Optional
import logging


class DatabaseConnection:
    """
    Singleton class for Supabase database connection.

    Lazily initializes a Supabase client and validates environment variables
    and connection. Supports optional external logging.
    """

    # Default environment variable details
    _env_location = "../../.env"
    _envar_url_name = "SUPABASE_URL"
    _envar_key_name = "SUPABASE_KEY"

    # Singleton and thread safety
    _lock = Lock()
    _instance = None

    client: Optional[Client] = None

    def __new__(cls, env_location: Optional[str] = None, logger: Optional[logging.Logger] = None):
        """
        Returns the singleton instance. Optionally override ..env location or pass a logger.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    if env_location:
                        cls._instance._env_location = env_location
                    cls._instance._logger = logger
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Loads environment variables, validates them, and creates the Supabase client.
        Also runs a flexible health check to confirm connectivity.
        """
        load_dotenv(os.path.join(os.path.dirname(__file__), self._env_location))

        self._envar_url = os.getenv(self._envar_url_name)
        self._envar_key = os.getenv(self._envar_key_name)
        self._validate_envars()

        self.client: Client = create_client(self._envar_url, self._envar_key)
        self._validate_connection()

    def _validate_envars(self):
        """
        Checks that required environment variables are set.
        Raises ValueError if missing.
        """
        if not self._envar_url:
            self._log_error(f"{self._envar_url_name} is missing in environment.")
            raise ValueError(f"{self._envar_url_name} must be set in environment variables.")
        if not self._envar_key:
            self._log_error(f"{self._envar_key_name} is missing in environment.")
            raise ValueError(f"{self._envar_key_name} must be set in environment variables.")

    def _validate_connection(self):
        """
        Flexible health check: tries to list tables, then fallback to select from 'lesson' table.
        Raises ConnectionError if Supabase cannot be reached.
        """
        try:
            # Try listing tables first (more generic)
            self.client.rpc("pg_tables").execute()
        except Exception:
            try:
                # Fallback: simple select from a known table
                self.client.table("lesson").select("lesson_id").limit(1).execute()
            except Exception as e:
                self._log_error(f"Supabase connection failed: {e}")
                raise ConnectionError(f"Failed to connect to Supabase: {e}")

    def _log_error(self, message: str):
        """
        Logs error message using external logger if provided, else prints to stderr.
        """
        if hasattr(self, "_logger") and self._logger:
            self._logger.error(message)
        else:
            print(f"[DatabaseConnection ERROR] {message}")

    def __repr__(self):
        return f"<DatabaseConnection client_initialized={self.client is not None}>"

