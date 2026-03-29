from backend.app.domain.person import extract_person_update_fields, prepare_person_linked_create
from backend.app.common.base import NotFoundError
from backend.app.infrastructure.database.models import Client
from backend.app.infrastructure.database.models import Person


def get_all_clients():
    return Client.get_all()


def list_clients(page: int = 1, page_size: int = 20, search: str = None):
    return Client.list(page, page_size, search)


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

    Two modes (enforced by domain layer):
      - Pass person_id to make an existing person a client.
      - Pass name (+ optional email/phone) to create a new person and client.
    """
    person_fields, client_data = prepare_person_linked_create(data)
    if person_fields is not None:
        person = Person.create(person_fields)
        client_data["person_id"] = person[0]["person_id"]
    return Client.create(client_data)


def update_client(client_id, data):
    person_fields, client_data = extract_person_update_fields(data)
    if person_fields:
        rows = Client.get(client_id)
        if rows:
            Person.update(rows[0]["person_id"], person_fields)
    if client_data:
        Client.update(client_id, client_data)
    return Client.get(client_id)


def delete_client(client_id):
    return Client.delete(client_id)
