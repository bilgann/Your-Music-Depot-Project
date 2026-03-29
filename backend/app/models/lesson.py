from backend.app.singletons.database import DatabaseConnection


class Lesson:
    def __init__(self, lesson_id, instructor_id, room_id,
                 start_time, end_time, student_id=None,
                 rate=None, status=None, recurrence=None):
        self.lesson_id = lesson_id
        self.student_id = student_id
        self.instructor_id = instructor_id
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time
        self.rate = rate
        self.status = status
        self.recurrence = recurrence

    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("lesson").select("*").execute().data

    @staticmethod
    def get(lesson_id):
        return (
            DatabaseConnection().client
            .table("lesson")
            .select("*")
            .eq("lesson_id", lesson_id)
            .execute()
            .data
        )

    @staticmethod
    def get_for_week(start, end):
        return (
            DatabaseConnection().client
            .table("lesson")
            .select("*")
            .gte("start_time", start)
            .lte("end_time", end)
            .execute()
            .data
        )

    @staticmethod
    def get_for_student_in_period(student_id, period_start, period_end, statuses: list):
        """
        Returns all lessons the student is enrolled in within the given period.
        Uses the lesson_enrollment join table as the source of truth.
        """
        enrollments = (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .select("lesson_id")
            .eq("student_id", student_id)
            .execute()
            .data
        )
        lesson_ids = [e["lesson_id"] for e in enrollments]
        if not lesson_ids:
            return []

        return (
            DatabaseConnection().client
            .table("lesson")
            .select("*")
            .in_("lesson_id", lesson_ids)
            .in_("status", statuses)
            .gte("start_time", period_start)
            .lte("start_time", period_end + "T23:59:59")
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("lesson").insert(data).execute().data

    @staticmethod
    def update(lesson_id, data):
        return (
            DatabaseConnection().client
            .table("lesson")
            .update(data)
            .eq("lesson_id", lesson_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(lesson_id):
        return (
            DatabaseConnection().client
            .table("lesson")
            .delete()
            .eq("lesson_id", lesson_id)
            .execute()
            .data
        )
