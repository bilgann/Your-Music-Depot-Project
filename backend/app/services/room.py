from backend.app.singletons.database import DatabaseConnection


def _db():
    return DatabaseConnection().client


def get_all_rooms():
    return _db().table("room").select("*").execute().data


def get_room_by_id(room_id):
    return _db().table("room").select("*").eq("room_id", room_id).execute().data


def create_room(data):
    return _db().table("room").insert(data).execute().data


def update_room(room_id, data):
    return _db().table("room").update(data).eq("room_id", room_id).execute().data


def delete_room(room_id):
    return _db().table("room").delete().eq("room_id", room_id).execute().data