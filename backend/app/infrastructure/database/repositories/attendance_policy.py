from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.AttendancePolicyEntity


class AttendancePolicy:
    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("attendance_policy").select("*").execute().data

    @staticmethod
    def get(policy_id):
        return (
            DatabaseConnection().client
            .table("attendance_policy")
            .select("*")
            .eq("policy_id", policy_id)
            .execute()
            .data
        )

    @staticmethod
    def get_default():
        rows = (
            DatabaseConnection().client
            .table("attendance_policy")
            .select("*")
            .eq("is_default", True)
            .limit(1)
            .execute()
            .data
        )
        return rows[0] if rows else None

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("attendance_policy").insert(data).execute().data

    @staticmethod
    def update(policy_id, data):
        return (
            DatabaseConnection().client
            .table("attendance_policy")
            .update(data)
            .eq("policy_id", policy_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(policy_id):
        return (
            DatabaseConnection().client
            .table("attendance_policy")
            .delete()
            .eq("policy_id", policy_id)
            .execute()
            .data
        )
