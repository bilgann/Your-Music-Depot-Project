from backend.app.infrastructure.database.database import DatabaseConnection

# No separate domain entity — Schedule is a query service, not a data object.


class Schedule:
    """Scheduling availability queries against the lesson table."""

    @staticmethod
    def get_instructor_conflicts(instructor_id, start_time, end_time):
        return (
            DatabaseConnection().client
            .table("lesson")
            .select("lesson_id, start_time, end_time")
            .eq("instructor_id", instructor_id)
            .lt("start_time", end_time)
            .gt("end_time", start_time)
            .execute()
            .data
        )

    @staticmethod
    def get_room_conflicts(room_id, start_time, end_time):
        return (
            DatabaseConnection().client
            .table("lesson")
            .select("lesson_id, start_time, end_time")
            .eq("room_id", room_id)
            .lt("start_time", end_time)
            .gt("end_time", start_time)
            .execute()
            .data
        )

    @staticmethod
    def instructor_available(instructor_id, start_time, end_time) -> bool:
        return len(Schedule.get_instructor_conflicts(instructor_id, start_time, end_time)) == 0

    @staticmethod
    def room_available(room_id, start_time, end_time) -> bool:
        return len(Schedule.get_room_conflicts(room_id, start_time, end_time)) == 0
