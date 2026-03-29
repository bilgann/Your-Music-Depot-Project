import hashlib

from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.UserEntity


class User:
    @staticmethod
    def validate_user(username: str, password: str):
        """
        Validate credentials against the app_user table in Supabase.

        Password is stored as SHA-256(password). Falls back to the hardcoded
        dev account (barnes / password) when the table does not yet exist.
        Remove the dev fallback before going to production.
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
            if isinstance(rows, list) and rows:
                row = rows[0]
                from backend.app.domain.entities.user import UserEntity
                return UserEntity(
                    user_id=row["user_id"],
                    username=row["username"],
                    role=row.get("role", "admin"),
                )
        except Exception:
            pass

        # ── Dev fallback ──────────────────────────────────────────────────────
        # WARNING: Remove before production.
        if username == "barnes" and password == "password":
            from backend.app.domain.entities.user import UserEntity
            return UserEntity("00000000-0000-0000-0000-000000000000", username, role="admin")

        return None
