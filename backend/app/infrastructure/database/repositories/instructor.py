from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.InstructorEntity
# Linked person: backend.app.domain.entities.PersonEntity


class Instructor:
    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("instructor").select("*").execute().data

    @staticmethod
    def list(page: int = 1, page_size: int = 20, search: str = None):
        offset = (page - 1) * page_size
        # Join person so callers get full name/contact data.
        # Name-based search is not supported here — instructor has no name column.
        q = DatabaseConnection().client.table("instructor").select("*, person(*)", count="exact")
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
