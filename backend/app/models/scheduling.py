from backend.app.singletons.database import DatabaseConnection


class Schedule:
    """Represents a scheduling query — checks instructor and room availability."""

    @staticmethod
    def get_instructor_conflicts(instructor_id, start_time, end_time):
        """Return lessons where the instructor is already booked in the given window."""
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
        """Return lessons where the room is already booked in the given window."""
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
