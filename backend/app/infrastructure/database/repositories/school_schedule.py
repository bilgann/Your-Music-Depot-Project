from backend.app.infrastructure.database.database import DatabaseConnection


class SchoolSchedule:
    @staticmethod
    def get_all():
        return (
            DatabaseConnection().client
            .table("school_schedule")
            .select("*")
            .order("created_at", desc=False)
            .execute()
            .data
        )

    @staticmethod
    def get_active():
        return (
            DatabaseConnection().client
            .table("school_schedule")
            .select("*")
            .eq("is_active", True)
            .order("created_at", desc=False)
            .execute()
            .data
        )

    @staticmethod
    def list(page: int = 1, page_size: int = 20, active_only: bool = False):
        offset = (page - 1) * page_size
        q = DatabaseConnection().client.table("school_schedule").select("*", count="exact")
        if active_only:
            q = q.eq("is_active", True)
        result = q.order("created_at", desc=False).range(offset, offset + page_size - 1).execute()
        return result.data, result.count

    @staticmethod
    def get(schedule_id):
        return (
            DatabaseConnection().client
            .table("school_schedule")
            .select("*")
            .eq("schedule_id", schedule_id)
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return (
            DatabaseConnection().client
            .table("school_schedule")
            .insert(data)
            .execute()
            .data
        )

    @staticmethod
    def update(schedule_id, data):
        return (
            DatabaseConnection().client
            .table("school_schedule")
            .update(data)
            .eq("schedule_id", schedule_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(schedule_id):
        return (
            DatabaseConnection().client
            .table("school_schedule")
            .delete()
            .eq("schedule_id", schedule_id)
            .execute()
            .data
        )
