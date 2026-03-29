from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.LessonOccurrenceEntity


class LessonOccurrence:
    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("lesson_occurrence").select("*").execute().data

    @staticmethod
    def get(occurrence_id):
        return (
            DatabaseConnection().client
            .table("lesson_occurrence")
            .select("*")
            .eq("occurrence_id", occurrence_id)
            .execute()
            .data
        )

    @staticmethod
    def get_by_lesson(lesson_id):
        return (
            DatabaseConnection().client
            .table("lesson_occurrence")
            .select("*")
            .eq("lesson_id", lesson_id)
            .order("date")
            .execute()
            .data
        )

    @staticmethod
    def get_by_course(course_id):
        return (
            DatabaseConnection().client
            .table("lesson_occurrence")
            .select("*")
            .eq("course_id", course_id)
            .order("date")
            .execute()
            .data
        )

    @staticmethod
    def get_by_instructor(instructor_id):
        return (
            DatabaseConnection().client
            .table("lesson_occurrence")
            .select("*")
            .eq("instructor_id", instructor_id)
            .order("date")
            .execute()
            .data
        )

    @staticmethod
    def get_in_range(start_date: str, end_date: str):
        return (
            DatabaseConnection().client
            .table("lesson_occurrence")
            .select("*")
            .gte("date", start_date)
            .lte("date", end_date)
            .order("date")
            .execute()
            .data
        )

    @staticmethod
    def get_for_student_in_period(student_id: str, period_start: str, period_end: str, statuses: list):
        """
        Return occurrences for a student within a date range with given statuses.
        Joins through lesson_enrollment on occurrence_id.
        """
        enrollments = (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .select("occurrence_id, attendance_status")
            .eq("student_id", student_id)
            .execute()
            .data
        )
        if not enrollments:
            return []

        occurrence_ids = [e["occurrence_id"] for e in enrollments]
        attendance_map = {e["occurrence_id"]: e.get("attendance_status") for e in enrollments}

        occurrences = (
            DatabaseConnection().client
            .table("lesson_occurrence")
            .select("*")
            .in_("occurrence_id", occurrence_ids)
            .in_("status", statuses)
            .gte("date", period_start)
            .lte("date", period_end)
            .execute()
            .data
        )

        for occ in occurrences:
            occ["attendance_status"] = attendance_map.get(occ["occurrence_id"])

        return occurrences

    @staticmethod
    def bulk_create(occurrences: list):
        if not occurrences:
            return []
        return DatabaseConnection().client.table("lesson_occurrence").insert(occurrences).execute().data

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("lesson_occurrence").insert(data).execute().data

    @staticmethod
    def update(occurrence_id, data):
        return (
            DatabaseConnection().client
            .table("lesson_occurrence")
            .update(data)
            .eq("occurrence_id", occurrence_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(occurrence_id):
        return (
            DatabaseConnection().client
            .table("lesson_occurrence")
            .delete()
            .eq("occurrence_id", occurrence_id)
            .execute()
            .data
        )

    @staticmethod
    def delete_by_lesson(lesson_id):
        return (
            DatabaseConnection().client
            .table("lesson_occurrence")
            .delete()
            .eq("lesson_id", lesson_id)
            .execute()
            .data
        )

    @staticmethod
    def delete_by_course(course_id):
        return (
            DatabaseConnection().client
            .table("lesson_occurrence")
            .delete()
            .eq("course_id", course_id)
            .execute()
            .data
        )
