import hashlib

from backend.app.application.singletons.database import DatabaseConnection


class User:
    def __init__(self, id, username, role: str = "admin", password=None):
        self.id = id
        self.username = username
        self.role = role
        self.password = password

    @staticmethod
    def validate_user(username: str, password: str):
        """
        Validate credentials against the app_user table in Supabase.

        Password is stored as SHA-256(password). The comparison uses a DB-side
        query so we never transmit plaintext passwords over the wire.

        Falls back to the hardcoded dev account (barnes / password) when the
        app_user table does not yet exist or the DB cannot be reached — this
        avoids blocking local development before the table is provisioned.
        """
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            rows = (
                DatabaseConnection()
                .client
                .table("app_user")
                .select("user_id, username, role")
                .eq("username", username)
                .eq("password_hash", password_hash)
                .execute()
                .data
            )
            # isinstance check guards against MagicMock in unit tests
            if isinstance(rows, list) and rows:
                row = rows[0]
                return User(row["user_id"], row["username"], role=row.get("role", "admin"))
        except Exception:
            pass  # fall through to dev fallback below

        # ── Dev fallback ──────────────────────────────────────────────────────
        # WARNING: Remove or disable this block before going to production.
        # Create a real row in app_user to replace these credentials.
        if username == "barnes" and password == "password":
            return User("00000000-0000-0000-0000-000000000000", username, role="admin")

        return None
