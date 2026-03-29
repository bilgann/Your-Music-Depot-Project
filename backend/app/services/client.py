from backend.app.exceptions.base import NotFoundError, ValidationError
from backend.app.models.client import Client
from backend.app.models.person import Person


def get_all_clients():
    return Client.get_all()


def get_client_by_id(client_id):
    return Client.get(client_id)


def get_client_students(client_id):
    rows = Client.get(client_id)
    if not rows:
        raise NotFoundError("Client not found.")
    return Client.get_students(client_id)


def create_client(data):
    """
    Create a client record.

    Two modes:
      - Pass person_id to make an existing person a client (e.g. a student becoming a billing contact).
      - Pass name (+ optional email/phone) to create a new person and client together.
    """
    data = dict(data)
    if "person_id" not in data or not data["person_id"]:
        if not data.get("name"):
            raise ValidationError([{"field": "name", "message": "name is required when person_id is not provided."}])
        person_data = {k: data.pop(k) for k in ("name", "email", "phone") if k in data}
        person = Person.create(person_data)
        data["person_id"] = person[0]["person_id"]
    else:
        data.pop("name", None)
        data.pop("email", None)
        data.pop("phone", None)

    return Client.create(data)


def update_client(client_id, data):
    data = dict(data)
    person_fields = {k: data.pop(k) for k in ("name", "email", "phone") if k in data}
    if person_fields:
        rows = Client.get(client_id)
        if rows:
            Person.update(rows[0]["person_id"], person_fields)
    if data:
        Client.update(client_id, data)
    return Client.get(client_id)


def delete_client(client_id):
    return Client.delete(client_id)
