from backend.app.domain.exceptions.exceptions import NotFoundError
from backend.app.infrastructure.database.repositories import Instructor


def _reshape(row: dict) -> dict:
    """Flatten person sub-object to top level so the frontend can read name/email/phone directly."""
    person = row.get("person") or {}
    return {
        **{k: v for k, v in row.items() if k != "person"},
        "name":  person.get("name"),
        "email": person.get("email"),
        "phone": person.get("phone"),
    }


def get_all_instructors():
    return [_reshape(r) for r in Instructor.get_all()]


def list_instructors(page: int = 1, page_size: int = 20, search: str = None):
    rows, total = Instructor.list(page, page_size, search)
    return [_reshape(r) for r in rows], total


def get_instructor_by_id(instructor_id):
    rows = Instructor.get(instructor_id)
    return [_reshape(r) for r in rows]


def create_instructor(data):
    return Instructor.create(data)


def update_instructor(instructor_id, data):
    if not Instructor.get(instructor_id):
        raise NotFoundError("Instructor not found.")
    return Instructor.update(instructor_id, data)


def delete_instructor(instructor_id):
    if not Instructor.get(instructor_id):
        raise NotFoundError("Instructor not found.")
    return Instructor.delete(instructor_id)
