from backend.app.singletons.database import DatabaseConnection

VALID_CHARGE_TYPES = {"none", "flat", "percentage"}


class AttendancePolicy:
    def __init__(self, policy_id, name,
                 absent_charge_type="none", absent_charge_value=0,
                 cancel_charge_type="none", cancel_charge_value=0,
                 late_cancel_charge_type="none", late_cancel_charge_value=0,
                 is_default=False):
        self.policy_id = policy_id
        self.name = name
        self.absent_charge_type = absent_charge_type
        self.absent_charge_value = absent_charge_value
        self.cancel_charge_type = cancel_charge_type
        self.cancel_charge_value = cancel_charge_value
        self.late_cancel_charge_type = late_cancel_charge_type
        self.late_cancel_charge_value = late_cancel_charge_value
        self.is_default = is_default

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
