from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.AuditLogEntity


class AuditLog:
    @staticmethod
    def list_filtered(entity_type=None, entity_id=None, limit=200):
        query = (
            DatabaseConnection().client
            .table("audit_log")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
        )
        if entity_type:
            query = query.eq("entity_type", entity_type)
        if entity_id:
            query = query.eq("entity_id", entity_id)
        return query.execute().data

    @staticmethod
    def get_by_entity(entity_type, entity_id):
        return (
            DatabaseConnection().client
            .table("audit_log")
            .select("*")
            .eq("entity_type", entity_type)
            .eq("entity_id", str(entity_id))
            .execute()
            .data
        )

    @staticmethod
    def get_by_user(user_id):
        return (
            DatabaseConnection().client
            .table("audit_log")
            .select("*")
            .eq("user_id", str(user_id))
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("audit_log").insert(data).execute().data
