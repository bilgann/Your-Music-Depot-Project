from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.LessonEntity

class Lesson:
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
            .lte("start_time", end + "T23:59:59")
            .execute()
            .data
        )

    @staticmethod
    def get_for_student_in_period(student_id, period_start, period_end, statuses: list):
        enrollments = (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .select("lesson_id, attendance_status")
            .eq("student_id", student_id)
            .execute()
            .data
        )
        if not enrollments:
            return []

        lesson_ids = [e["lesson_id"] for e in enrollments]
        attendance_map = {e["lesson_id"]: e.get("attendance_status") for e in enrollments}

        lessons = (
            DatabaseConnection().client
            .table("lesson")
            .select("*, attendance_policy(*)")
            .in_("lesson_id", lesson_ids)
            .in_("status", statuses)
            .gte("start_time", period_start)
            .lte("start_time", period_end + "T23:59:59")
            .execute()
            .data
        )

        for lesson in lessons:
            lesson["attendance_status"] = attendance_map.get(lesson["lesson_id"])

        return lessons

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
