from backend.app.application.singletons.database import DatabaseConnection


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
            .select("*, person(*), client(client_id, person(name))")
            .execute()
            .data
        )

    @staticmethod
    def list(page: int = 1, page_size: int = 20, search: str = None):
        offset = (page - 1) * page_size
        q = DatabaseConnection().client.table("student").select("*, person!inner(*), client(client_id, person(name))", count="exact")
        if search:
            q = q.ilike("person.name", f"%{search}%")
        result = q.range(offset, offset + page_size - 1).execute()
        return result.data, result.count

    @staticmethod
    def get(student_id):
        return (
            DatabaseConnection().client
            .table("student")
            .select("*, person(*), client(client_id, person(name))")
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
