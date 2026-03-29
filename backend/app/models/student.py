from backend.app.singletons.database import DatabaseConnection


class Student:
    def __init__(self, student_id, name, email=None, phone=None):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.phone = phone

    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("student").select("*").execute().data

    @staticmethod
    def get(student_id):
        return (
            DatabaseConnection().client
            .table("student")
            .select("*")
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("student").insert(data).execute().data

    @staticmethod
    def update(student_id, data):
        return (
            DatabaseConnection().client
            .table("student")
            .update(data)
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(student_id):
        return (
            DatabaseConnection().client
            .table("student")
            .delete()
            .eq("student_id", student_id)
            .execute()
            .data
        )
