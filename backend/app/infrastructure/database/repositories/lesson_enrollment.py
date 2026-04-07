from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.LessonEnrollmentEntity


class LessonEnrollment:
    @staticmethod
    def get_by_occurrence(occurrence_id):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .select("*, student(*)")
            .eq("occurrence_id", occurrence_id)
            .execute()
            .data
        )

    @staticmethod
    def get_by_student(student_id):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .select("*, lesson_occurrence(*, lesson(*), course(*), instructor(*, person(name)), room(name))")
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def get(occurrence_id, student_id):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .select("*")
            .eq("occurrence_id", occurrence_id)
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def create(occurrence_id, student_id):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .insert({"occurrence_id": occurrence_id, "student_id": student_id})
            .execute()
            .data
        )

    @staticmethod
    def record_attendance(occurrence_id, student_id, status):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .update({"attendance_status": status})
            .eq("occurrence_id", occurrence_id)
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(occurrence_id, student_id):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .delete()
            .eq("occurrence_id", occurrence_id)
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def delete_by_occurrence(occurrence_id):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .delete()
            .eq("occurrence_id", occurrence_id)
            .execute()
            .data
        )
