from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.InstructorStudentCompatibilityEntity


class InstructorStudentCompatibility:
    @staticmethod
    def get_by_student(student_id):
        return (
            DatabaseConnection().client
            .table("instructor_student_compatibility")
            .select("*")
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def get_by_instructor(instructor_id):
        return (
            DatabaseConnection().client
            .table("instructor_student_compatibility")
            .select("*")
            .eq("instructor_id", instructor_id)
            .execute()
            .data
        )

    @staticmethod
    def get(instructor_id, student_id):
        return (
            DatabaseConnection().client
            .table("instructor_student_compatibility")
            .select("*")
            .eq("instructor_id", instructor_id)
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return (
            DatabaseConnection().client
            .table("instructor_student_compatibility")
            .insert(data)
            .execute()
            .data
        )

    @staticmethod
    def update(compatibility_id, data):
        return (
            DatabaseConnection().client
            .table("instructor_student_compatibility")
            .update(data)
            .eq("compatibility_id", compatibility_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(compatibility_id):
        return (
            DatabaseConnection().client
            .table("instructor_student_compatibility")
            .delete()
            .eq("compatibility_id", compatibility_id)
            .execute()
            .data
        )
