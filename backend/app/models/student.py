from backend.app.singletons.database import DatabaseConnection


class Student:
    def __init__(self, student_id, person_id, client_id=None):
        self.student_id = student_id
        self.person_id = person_id
        self.client_id = client_id

    @staticmethod
    def get_all():
        return (
            DatabaseConnection().client
            .table("student")
            .select("*, person(*)")
            .execute()
            .data
        )

    @staticmethod
    def get(student_id):
        return (
            DatabaseConnection().client
            .table("student")
            .select("*, person(*)")
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
