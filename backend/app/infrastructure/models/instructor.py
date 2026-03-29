from backend.app.application.singletons.database import DatabaseConnection


class Instructor:
    def __init__(self, instructor_id, name, email=None, phone=None):
        self.instructor_id = instructor_id
        self.name = name
        self.email = email
        self.phone = phone

    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("instructor").select("*").execute().data

    @staticmethod
    def list(page: int = 1, page_size: int = 20, search: str = None):
        offset = (page - 1) * page_size
        q = DatabaseConnection().client.table("instructor").select("*", count="exact")
        if search:
            q = q.ilike("name", f"%{search}%")
        result = q.range(offset, offset + page_size - 1).execute()
        return result.data, result.count

    @staticmethod
    def get(instructor_id):
        return (
            DatabaseConnection().client
            .table("instructor")
            .select("*")
            .eq("instructor_id", instructor_id)
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("instructor").insert(data).execute().data

    @staticmethod
    def update(instructor_id, data):
        return (
            DatabaseConnection().client
            .table("instructor")
            .update(data)
            .eq("instructor_id", instructor_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(instructor_id):
        return (
            DatabaseConnection().client
            .table("instructor")
            .delete()
            .eq("instructor_id", instructor_id)
            .execute()
            .data
        )
