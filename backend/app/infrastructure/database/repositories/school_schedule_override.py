from backend.app.infrastructure.database.database import DatabaseConnection


class SchoolScheduleOverride:
    @staticmethod
    def get_by_schedule(schedule_id):
        return (
            DatabaseConnection().client
            .table("school_schedule_override")
            .select("*")
            .eq("schedule_id", schedule_id)
            .order("created_at", desc=False)
            .execute()
            .data
        )

    @staticmethod
    def get_for_schedules(schedule_ids: list[str]):
        """Load all overrides for a list of schedule IDs in one query."""
        if not schedule_ids:
            return []
        return (
            DatabaseConnection().client
            .table("school_schedule_override")
            .select("*")
            .in_("schedule_id", schedule_ids)
            .execute()
            .data
        )

    @staticmethod
    def get(override_id):
        return (
            DatabaseConnection().client
            .table("school_schedule_override")
            .select("*")
            .eq("override_id", override_id)
            .execute()
            .data
        )

    @staticmethod
    def find(schedule_id, entity_type, entity_id):
        """Check if a specific override exists."""
        return (
            DatabaseConnection().client
            .table("school_schedule_override")
            .select("*")
            .eq("schedule_id", schedule_id)
            .eq("entity_type", entity_type)
            .eq("entity_id", entity_id)
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return (
            DatabaseConnection().client
            .table("school_schedule_override")
            .insert(data)
            .execute()
            .data
        )

    @staticmethod
    def delete(override_id):
        return (
            DatabaseConnection().client
            .table("school_schedule_override")
            .delete()
            .eq("override_id", override_id)
            .execute()
            .data
        )
