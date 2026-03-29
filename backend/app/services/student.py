from backend.app.exceptions.base import ValidationError
from backend.app.models.invoice import Invoice
from backend.app.models.lesson_enrollment import LessonEnrollment
from backend.app.models.person import Person
from backend.app.models.student import Student


def get_all_students():
    return Student.get_all()


def get_student_by_id(student_id):
    return Student.get(student_id)


def create_student(data):
    """
    Create a student record.

    Two modes:
      - Pass person_id to link an existing person as a student.
      - Pass name (+ optional email/phone) to create a new person and student together.
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

    return Student.create(data)


def update_student(student_id, data):
    data = dict(data)
    person_fields = {k: data.pop(k) for k in ("name", "email", "phone") if k in data}
    if person_fields:
        rows = Student.get(student_id)
        if rows:
            Person.update(rows[0]["person_id"], person_fields)
    if data:
        Student.update(student_id, data)
    return Student.get(student_id)


def delete_student(student_id):
    return Student.delete(student_id)


def get_student_lessons(student_id):
    return LessonEnrollment.get_by_student(student_id)


def get_student_invoices(student_id):
    return Invoice.get_by_student(student_id)
