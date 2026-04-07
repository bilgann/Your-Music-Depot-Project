from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.CourseEntity


class Course:
    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("course").select("*").execute().data

    @staticmethod
    def get(course_id):
        return (
            DatabaseConnection().client
            .table("course")
            .select("*")
            .eq("course_id", course_id)
            .execute()
            .data
        )

    @staticmethod
    def get_by_instructor(instructor_id):
        return (
            DatabaseConnection().client
            .table("course")
            .select("*")
            .contains("instructor_ids", [instructor_id])
            .execute()
            .data
        )

    @staticmethod
    def get_by_student(student_id):
        return (
            DatabaseConnection().client
            .table("course")
            .select("*")
            .contains("student_ids", [student_id])
            .execute()
            .data
        )

    @staticmethod
    def get_active():
        return (
            DatabaseConnection().client
            .table("course")
            .select("*")
            .eq("status", "active")
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("course").insert(data).execute().data

    @staticmethod
    def update(course_id, data):
        return (
            DatabaseConnection().client
            .table("course")
            .update(data)
            .eq("course_id", course_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(course_id):
        return (
            DatabaseConnection().client
            .table("course")
            .delete()
            .eq("course_id", course_id)
            .execute()
            .data
        )
