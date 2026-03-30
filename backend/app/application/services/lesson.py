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


def get_occurrences_for_range(start, end):
    """Return lesson occurrences in a date range with combined date+time fields."""
    rows = LessonOccurrence.get_in_range(start, end)
    for row in rows:
        d = row.get("date", "")
        st = row.get("start_time", "")
        et = row.get("end_time", "")
        row["start_datetime"] = f"{d}T{st}" if d and st else st
        row["end_datetime"]   = f"{d}T{et}" if d and et else et
    return rows


def get_lesson_by_id(lesson_id):
    return Lesson.get(lesson_id)


def get_occurrences_for_lesson(lesson_id):
    """Return all projected occurrences for a given lesson."""
    return LessonOccurrence.get_by_lesson(lesson_id)


_LESSON_COLUMNS = {
    "instructor_id", "room_id", "start_time", "end_time",
    "status", "rate", "recurrence", "student_ids", "course_id",
}


def _clean_payload(data: dict) -> dict:
    """Strip fields that don't map to lesson table columns."""
    return {k: v for k, v in data.items() if k in _LESSON_COLUMNS}


def create_lesson(data):
    return Lesson.create(_clean_payload(data))


def update_lesson(lesson_id, data):
    return Lesson.update(lesson_id, _clean_payload(data))


def delete_lesson(lesson_id):
    # Remove projected occurrences and their enrollments.
    for occ in LessonOccurrence.get_by_lesson(lesson_id):
        LessonEnrollment.delete_by_occurrence(occ["occurrence_id"])
    LessonOccurrence.delete_by_lesson(lesson_id)
    return Lesson.delete(lesson_id)


# ── Schedule projection ───────────────────────────────────────────────────────

def project_lesson_schedule(lesson_id: str, period_start: str = "", period_end: str = "") -> list:
    """
    Expand the lesson's recurrence rule into LessonOccurrenceEntity stubs,
    collect blocked_times from all participants, and persist the result.

    Idempotent: existing occurrences for this lesson are deleted first.
    """
    from datetime import date, timedelta
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

    # School-wide blocked times (holidays, vacations) — filtered by overrides.
    from backend.app.application.services.school_schedule import collect_school_blocked_times
    blocked.extend(collect_school_blocked_times([
        ("lesson", lesson.lesson_id),
        ("instructor", lesson.instructor_id),
        ("room", lesson.room_id),
    ]))

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

    # Use provided period or default to today → 3 months out.
    start_date = period_start or rows[0].get("period_start", "")
    end_date   = period_end   or rows[0].get("period_end",   "")
    if not start_date or not end_date:
        today = date.today()
        start_date = start_date or today.isoformat()
        end_date   = end_date   or (today + timedelta(days=90)).isoformat()
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
