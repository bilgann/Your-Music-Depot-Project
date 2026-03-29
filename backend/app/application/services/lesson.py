from backend.app.domain.exceptions.exceptions import ConflictError, NotFoundError
from backend.app.infrastructure.database.repositories import Lesson
from backend.app.infrastructure.database.repositories import LessonEnrollment


def get_all_lessons():
    return Lesson.get_all()


def get_lessons_for_week(start, end):
    return Lesson.get_for_week(start, end)


def get_lesson_by_id(lesson_id):
    return Lesson.get(lesson_id)


def create_lesson(data):
    return Lesson.create(data)


def update_lesson(lesson_id, data):
    return Lesson.update(lesson_id, data)


def delete_lesson(lesson_id):
    return Lesson.delete(lesson_id)


# ── Enrollment ────────────────────────────────────────────────────────────────

def get_lesson_students(lesson_id):
    rows = Lesson.get(lesson_id)
    if not rows:
        raise NotFoundError("Lesson not found.")
    return LessonEnrollment.get_by_lesson(lesson_id)


def enroll_student(lesson_id, student_id):
    rows = Lesson.get(lesson_id)
    if not rows:
        raise NotFoundError("Lesson not found.")
    existing = LessonEnrollment.get(lesson_id, student_id)
    if existing:
        raise ConflictError("Student is already enrolled in this lesson.")
    return LessonEnrollment.create(lesson_id, student_id)


def record_attendance(lesson_id, student_id, status):
    existing = LessonEnrollment.get(lesson_id, student_id)
    if not existing:
        raise NotFoundError("Enrollment not found.")
    return LessonEnrollment.record_attendance(lesson_id, student_id, status)


def unenroll_student(lesson_id, student_id):
    existing = LessonEnrollment.get(lesson_id, student_id)
    if not existing:
        raise NotFoundError("Enrollment not found.")
    return LessonEnrollment.delete(lesson_id, student_id)
