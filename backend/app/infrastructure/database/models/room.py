from backend.app.application.singletons.database import DatabaseConnection


class Room:
    def __init__(self, room_id, name, capacity=None):
        self.room_id = room_id
        self.name = name
        self.capacity = capacity

    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("room").select("*").execute().data

    @staticmethod
    def list(page: int = 1, page_size: int = 20, search: str = None):
        offset = (page - 1) * page_size
        q = DatabaseConnection().client.table("room").select("*", count="exact")
        if search:
            q = q.ilike("name", f"%{search}%")
        result = q.range(offset, offset + page_size - 1).execute()
        return result.data, result.count

    @staticmethod
    def get(room_id):
        return (
            DatabaseConnection().client
            .table("room")
            .select("*")
            .eq("room_id", room_id)
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("room").insert(data).execute().data

    @staticmethod
    def update(room_id, data):
        return (
            DatabaseConnection().client
            .table("room")
            .update(data)
            .eq("room_id", room_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(room_id):
        return (
            DatabaseConnection().client
            .table("room")
            .delete()
            .eq("room_id", room_id)
            .execute()
            .data
        )
