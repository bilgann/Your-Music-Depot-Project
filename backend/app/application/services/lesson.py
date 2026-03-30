import uuid

from backend.app.domain.exceptions.exceptions import ConflictError, NotFoundError
from backend.app.domain.services import schedule_projection
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
from backend.app.infrastructure.database.repositories import (
    Client,
    Instructor,
    Lesson,
    LessonEnrollment,
    LessonOccurrence,
    Room,
    Student,
)


# ── Lesson template CRUD ──────────────────────────────────────────────────────

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
    # Remove projected occurrences and their enrollments.
    for occ in LessonOccurrence.get_by_lesson(lesson_id):
        LessonEnrollment.delete_by_occurrence(occ["occurrence_id"])
    LessonOccurrence.delete_by_lesson(lesson_id)
    return Lesson.delete(lesson_id)


# ── Schedule projection ───────────────────────────────────────────────────────

def project_lesson_schedule(lesson_id: str) -> list:
    """
    Expand the lesson's recurrence rule into LessonOccurrenceEntity stubs,
    collect blocked_times from all participants, and persist the result.

    Idempotent: existing occurrences for this lesson are deleted first.
    """
    from backend.app.domain.entities.lesson import LessonEntity
    from backend.app.domain.entities.instructor import InstructorEntity
    from backend.app.domain.entities.room import RoomEntity
    from backend.app.domain.entities.client import ClientEntity
    from backend.app.domain.value_objects.scheduling.date_range import DateRange

    rows = Lesson.get(lesson_id)
    if not rows:
        raise NotFoundError("Lesson not found.")

    lesson = LessonEntity.from_dict(rows[0])
    if not lesson.recurrence:
        raise ConflictError("Lesson has no recurrence rule — cannot project occurrences.")

    blocked: list[BlockedTime] = []

    irows = Instructor.get(lesson.instructor_id)
    if irows:
        entity = InstructorEntity.from_dict(irows[0])
        blocked.extend(entity.blocked_times)

    rrows = Room.get(lesson.room_id)
    if rrows:
        entity = RoomEntity.from_dict(rrows[0])
        blocked.extend(entity.blocked_times)

    for sid in lesson.student_ids:
        srows = Student.get(sid)
        if srows and srows[0].get("client_id"):
            crows = Client.get(srows[0]["client_id"])
            if crows:
                entity = ClientEntity.from_dict(crows[0])
                blocked.extend(entity.blocked_times)

    # Use the lesson's period dates as the projection window.
    start_date = rows[0].get("period_start", "")
    end_date   = rows[0].get("period_end",   "")
    window = DateRange(period_start=start_date, period_end=end_date)

    # Re-project: delete existing first.
    for occ in LessonOccurrence.get_by_lesson(lesson_id):
        LessonEnrollment.delete_by_occurrence(occ["occurrence_id"])
    LessonOccurrence.delete_by_lesson(lesson_id)

    stubs = schedule_projection.project_occurrences(lesson, window, blocked)
    if not stubs:
        return []

    rows_to_insert = []
    for stub in stubs:
        d = stub.to_dict()
        d["occurrence_id"] = str(uuid.uuid4())
        rows_to_insert.append(d)

    saved = LessonOccurrence.bulk_create(rows_to_insert)

    # Auto-enroll lesson students into every new occurrence.
    if lesson.student_ids and saved:
        for occ in saved:
            for sid in lesson.student_ids:
                LessonEnrollment.create(occ["occurrence_id"], sid)

    return saved


# ── Occurrence enrollment ─────────────────────────────────────────────────────

def get_occurrence_students(occurrence_id):
    rows = LessonOccurrence.get(occurrence_id)
    if not rows:
        raise NotFoundError("Occurrence not found.")
    return LessonEnrollment.get_by_occurrence(occurrence_id)


def enroll_student_in_occurrence(occurrence_id, student_id):
    if not LessonOccurrence.get(occurrence_id):
        raise NotFoundError("Occurrence not found.")
    if LessonEnrollment.get(occurrence_id, student_id):
        raise ConflictError("Student is already enrolled in this occurrence.")
    return LessonEnrollment.create(occurrence_id, student_id)


def record_attendance(occurrence_id, student_id, status):
    if not LessonEnrollment.get(occurrence_id, student_id):
        raise NotFoundError("Enrollment not found.")
    return LessonEnrollment.record_attendance(occurrence_id, student_id, status)


def unenroll_student_from_occurrence(occurrence_id, student_id):
    if not LessonEnrollment.get(occurrence_id, student_id):
        raise NotFoundError("Enrollment not found.")
    return LessonEnrollment.delete(occurrence_id, student_id)
