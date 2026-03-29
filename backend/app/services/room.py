from backend.app.models.room import Room


def get_all_rooms():
    return Room.get_all()


def get_room_by_id(room_id):
    return Room.get(room_id)


def create_room(data):
    return Room.create(data)


def update_room(room_id, data):
    return Room.update(room_id, data)


def delete_room(room_id):
    return Room.delete(room_id)
