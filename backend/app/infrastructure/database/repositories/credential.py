from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.CredentialEntity


class Credential:
    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("credential").select("*").execute().data

    @staticmethod
    def get(credential_id):
        return (
            DatabaseConnection().client
            .table("credential")
            .select("*")
            .eq("credential_id", credential_id)
            .execute()
            .data
        )

    @staticmethod
    def get_by_instructor(instructor_id):
        return (
            DatabaseConnection().client
            .table("credential")
            .select("*")
            .eq("instructor_id", instructor_id)
            .execute()
            .data
        )

    @staticmethod
    def get_active_by_instructor(instructor_id):
        """Return credentials that have not expired (valid_until is null or in the future)."""
        from datetime import date
        today = date.today().isoformat()
        rows = (
            DatabaseConnection().client
            .table("credential")
            .select("*")
            .eq("instructor_id", instructor_id)
            .execute()
            .data
        )
        return [
            r for r in rows
            if r.get("valid_until") is None or r["valid_until"] >= today
        ]

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("credential").insert(data).execute().data

    @staticmethod
    def update(credential_id, data):
        return (
            DatabaseConnection().client
            .table("credential")
            .update(data)
            .eq("credential_id", credential_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(credential_id):
        return (
            DatabaseConnection().client
            .table("credential")
            .delete()
            .eq("credential_id", credential_id)
            .execute()
            .data
        )
