from backend.app.singletons.database import DatabaseConnection


class LessonEnrollment:
    def __init__(self, enrollment_id, lesson_id, student_id, enrolled_at=None):
        self.enrollment_id = enrollment_id
        self.lesson_id = lesson_id
        self.student_id = student_id
        self.enrolled_at = enrolled_at

    @staticmethod
    def get_by_lesson(lesson_id):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .select("*, student(*)")
            .eq("lesson_id", lesson_id)
            .execute()
            .data
        )

    @staticmethod
    def get_by_student(student_id):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .select("*, lesson(*, instructor(*), room(*))")
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def get(lesson_id, student_id):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .select("*")
            .eq("lesson_id", lesson_id)
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def create(lesson_id, student_id):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .insert({"lesson_id": lesson_id, "student_id": student_id})
            .execute()
            .data
        )

    @staticmethod
    def record_attendance(lesson_id, student_id, status):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .update({"attendance_status": status})
            .eq("lesson_id", lesson_id)
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(lesson_id, student_id):
        return (
            DatabaseConnection().client
            .table("lesson_enrollment")
            .delete()
            .eq("lesson_id", lesson_id)
            .eq("student_id", student_id)
            .execute()
            .data
        )
