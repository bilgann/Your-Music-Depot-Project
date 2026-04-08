from backend.app.domain.services.person import extract_person_update_fields, prepare_person_linked_create
from backend.app.domain.exceptions.exceptions import NotFoundError
from backend.app.infrastructure.database.repositories import Client
from backend.app.infrastructure.database.repositories import Invoice
from backend.app.infrastructure.database.repositories import LessonEnrollment
from backend.app.infrastructure.database.repositories import Person
from backend.app.infrastructure.database.repositories import Student


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
    from backend.app.domain.exceptions.exceptions import ValidationError as _VE
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
    rows = LessonEnrollment.get_by_student(student_id)
    return [_reshape_enrollment(r) for r in rows]


def get_student_timetable(student_id: str, start: str, end: str):
    """Return reshaped enrollments filtered to a date range."""
    rows = LessonEnrollment.get_by_student(student_id)
    filtered = [
        r for r in rows
        if start <= (r.get("lesson_occurrence") or {}).get("date", "") <= end
    ]
    return [_reshape_enrollment(r) for r in filtered]


def _reshape_enrollment(row: dict) -> dict:
    """Flatten lesson_occurrence into the shape the frontend expects."""
    occ = row.get("lesson_occurrence") or {}
    raw_instructor = occ.get("instructor") or {}
    person = raw_instructor.get("person") or {}
    instructor_name = person.get("name")
    raw_room = occ.get("room") or {}
    occ_date = occ.get("date", "")
    occ_start = occ.get("start_time", "")
    occ_end   = occ.get("end_time", "")
    start_dt = f"{occ_date}T{occ_start}" if occ_date and occ_start else occ_start
    end_dt   = f"{occ_date}T{occ_end}"   if occ_date and occ_end   else occ_end
    return {
        "enrollment_id":    row.get("enrollment_id"),
        "attendance_status": row.get("attendance_status"),
        "enrolled_at":       row.get("enrolled_at"),
        "lesson": {
            "lesson_id":   occ.get("occurrence_id"),
            "start_time":  start_dt,
            "end_time":    end_dt,
            "status":      occ.get("status"),
            "rate":        occ.get("rate"),
            "instructor":  {"name": instructor_name} if instructor_name else None,
            "room":        {"name": raw_room["name"]} if raw_room.get("name") else None,
        },
    }


def get_student_invoices(student_id):
    return Invoice.get_by_student(student_id)
