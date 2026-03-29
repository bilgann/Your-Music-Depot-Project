from backend.app.singletons.database import DatabaseConnection


class AuditLog:
    def __init__(self, log_id, user_id, action, entity_type, entity_id=None, old_value=None, new_value=None):
        self.log_id = log_id
        self.user_id = user_id
        self.action = action
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.old_value = old_value
        self.new_value = new_value

    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("audit_log").select("*").execute().data

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
