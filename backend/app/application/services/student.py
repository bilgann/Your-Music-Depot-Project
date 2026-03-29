from backend.app.domain.person import extract_person_update_fields, prepare_person_linked_create
from backend.app.common.base import NotFoundError
from backend.app.infrastructure.models import Client
from backend.app.infrastructure.models import Invoice
from backend.app.infrastructure.models import LessonEnrollment
from backend.app.infrastructure.models import Person
from backend.app.infrastructure.models import Student


def get_all_students():
    return Student.get_all()


def list_students(page: int = 1, page_size: int = 20, search: str = None):
    return Student.list(page, page_size, search)


def get_student_by_id(student_id):
    return Student.get(student_id)


def _validate_client_exists(client_id: str) -> None:
    if not Client.get(client_id):
        raise NotFoundError(f"Client {client_id} not found.")


def create_student(data):
    """
    Create a student record.

    Two modes (enforced by domain layer):
      - Pass person_id to link an existing person as a student.
      - Pass name (+ optional email/phone) to create a new person and student.

    client_id is required and must reference an existing client.
    Person/name validation runs first so callers receive the most relevant error.
    """
    from backend.app.common.base import ValidationError as _VE
    person_fields, student_data = prepare_person_linked_create(data)
    client_id = student_data.get("client_id")
    if not client_id:
        raise _VE([{"field": "client_id", "message": "client_id is required."}])
    _validate_client_exists(client_id)
    if person_fields is not None:
        person = Person.create(person_fields)
        student_data["person_id"] = person[0]["person_id"]
    return Student.create(student_data)


def update_student(student_id, data):
    if "client_id" in data:
        _validate_client_exists(data["client_id"])
    person_fields, student_data = extract_person_update_fields(data)
    if person_fields:
        rows = Student.get(student_id)
        if rows:
            Person.update(rows[0]["person_id"], person_fields)
    if student_data:
        Student.update(student_id, student_data)
    return Student.get(student_id)


def delete_student(student_id):
    return Student.delete(student_id)


def get_student_lessons(student_id):
    return LessonEnrollment.get_by_student(student_id)


def get_student_invoices(student_id):
    return Invoice.get_by_student(student_id)
