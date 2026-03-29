from backend.app.infrastructure.database.repositories import Room


def get_all_rooms():
    return Room.get_all()


def list_rooms(page: int = 1, page_size: int = 20, search: str = None):
    return Room.list(page, page_size, search)


def get_room_by_id(room_id):
    return Room.get(room_id)


def create_room(data):
    return Room.create(data)


def update_room(room_id, data):
    return Room.update(room_id, data)


def delete_room(room_id):
    return Room.delete(room_id)
