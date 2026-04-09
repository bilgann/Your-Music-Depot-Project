import uuid

from backend.app.domain.exceptions.exceptions import ConflictError, NotFoundError
from backend.app.domain.services import schedule_projection
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
from backend.app.infrastructure.database.database import DatabaseConnection
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

def _db():
    return DatabaseConnection().client


def _check_time_overlap(start1, end1, start2, end2):
    """
    Check if two time ranges overlap.
    Returns True if there's any overlap.
    """
    return start1 < end2 and end1 > start2


def _recurrences_can_overlap(rec1, rec2):
    """
    Return True if two recurrence strings could produce occurrences on the same date.
    Conservative: returns True when undetermined.

    Supported formats:
      - ISO date "YYYY-MM-DD" (one-time)
      - 5-field cron "min hour dom month dow" where dow is day-of-week (e.g. "MON,WED")
    """
    import re
    from datetime import date as _date

    if not rec1 or not rec2:
        return True  # no recurrence info → assume possible conflict

    _WEEKDAY_NAMES = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    def _parse(rec):
        rec = rec.strip()
        parts = rec.split()
        if len(parts) == 5:
            dow = parts[4].upper()
            if dow == "*":
                return "daily", None
            return "weekly", set(dow.split(","))
        if re.match(r"^\d{4}-\d{2}-\d{2}$", rec):
            try:
                d = _date.fromisoformat(rec)
                return "date", _WEEKDAY_NAMES[d.weekday()]
            except ValueError:
                pass
        return None, None

    t1, v1 = _parse(rec1)
    t2, v2 = _parse(rec2)

    if t1 is None or t2 is None:
        return True  # can't determine — conservative

    if t1 == "daily" or t2 == "daily":
        return True

    if t1 == "date" and t2 == "date":
        return rec1.strip() == rec2.strip()

    if t1 == "date" and t2 == "weekly":
        return v1 in v2

    if t1 == "weekly" and t2 == "date":
        return v2 in v1

    # Both weekly — conflict only if they share at least one weekday
    return bool(v1 & v2)


def _first_present(record, keys, default=None):
    for key in keys:
        if key in record and record[key] is not None:
            return record[key]
    return default


def _to_int(value):
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None

def _check_instructor_has_skill(instructor_id, instrument):
    """
    Check if instructor has the required skill/instrument certification.
    Queries instructor_skill table for a matching record.
    Returns (has_skill, instructor_skill_record) tuple.
    """
    if not instrument or not instructor_id:
        return False, None
    
    try:
        # Query instructor_skill table for all instructor skills and match skill/instrument locally
        response = _db().table("instructor_skill").select("*").eq("instructor_id", instructor_id).execute()
        rows = response.data or []

        instrument_norm = str(instrument).strip().lower()
        for row in rows:
            row_skill = _first_present(row, ["skill", "instrument", "skill_name"], "")
            if str(row_skill).strip().lower() == instrument_norm:
                return True, row

        return False, None
    except Exception as e:
        # Table might not exist or query failed - log and return error
        print(f"[skill_matching] Error checking instructor skill: {e}")
        return False, None


def _get_student_skill_record(student_id, instrument):
    """
    Get the student's skill record for the given instrument from student_skill.
    Returns the matching row or None.
    """
    if not student_id or not instrument:
        return None

    try:
        response = _db().table("student_skill").select("*").eq("student_id", student_id).execute()
        rows = response.data or []

        instrument_norm = str(instrument).strip().lower()
        for row in rows:
            row_skill = _first_present(row, ["skill", "instrument", "skill_name"], "")
            if str(row_skill).strip().lower() == instrument_norm:
                return row

        return None
    except Exception as e:
        print(f"[skill_matching] Error checking student skill: {e}")
        return None


def _check_skill_level_match(instructor_skill_row, student_skill_row):
    """
    Validate instructor minimum required level <= student's level.
    Returns (is_valid, instructor_min, student_level).
    """
    instructor_min = _to_int(_first_present(instructor_skill_row, ["min_skill_level", "minimum_skill_level", "min_level"]))
    student_level = _to_int(_first_present(student_skill_row, ["skill_level", "level", "student_skill_level"]))

    if instructor_min is None or student_level is None:
        return False, instructor_min, student_level

    return instructor_min <= student_level, instructor_min, student_level


def _get_instructor_name(instructor_id):
    """
    Helper to get instructor name by ID.
    Falls back to ID if name not available.
    """
    try:
        response = _db().table("instructor").select("*").eq("instructor_id", instructor_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0].get("name") or f"Instructor {instructor_id}"
        return f"Instructor {instructor_id}"
    except Exception:
        return f"Instructor {instructor_id}"

def _format_time(time_str):
    """
    Format a time string to HH:MM format.
    Handles ISO format strings like "2024-01-15T10:00:00" or simple "10:00".
    """
    if not time_str:
        return "unknown"
    try:
        # If it's an ISO format datetime
        if "T" in str(time_str):
            return str(time_str).split("T")[1][:5]
        # If it's already just time
        return str(time_str)[:5]
    except Exception:
        return str(time_str)


def _get_resource_name(lesson, resource_type):
    """
    Extract resource name from lesson data.
    Falls back to ID if name not available.
    """
    if resource_type == "instructor":
        return lesson.get("instructor_name") or f"Instructor {lesson.get('instructor_id')}"
    elif resource_type == "room":
        return lesson.get("room_name") or f"Room {lesson.get('room_id')}"
    elif resource_type == "student":
        return lesson.get("student_name") or f"Student {lesson.get('student_id')}"
    return "Unknown"


def _format_conflict_message(resource_type, resource_name, start_time, end_time):
    """
    Format a conflict message with resource and time.
    E.g., "Room Studio A is already booked 10:00–11:00"
    """
    start = _format_time(start_time)
    end = _format_time(end_time)
    
    if resource_type == "instructor":
        return f"{resource_name} is already teaching {start}–{end}"
    elif resource_type == "room":
        return f"{resource_name} is already booked {start}–{end}"
    elif resource_type == "student":
        return f"{resource_name} already has a lesson {start}–{end}"
    
    return f"{resource_name} conflicts {start}–{end}"


def _check_instructor_overlap(instructor_id, start_time, end_time, recurrence=None, exclude_lesson_id=None):
    """
    Check if instructor has overlapping lessons on the same schedule.
    Returns list of conflict messages, excluding current lesson if specified.
    """
    try:
        lessons = _db().table("lesson").select("*").eq("instructor_id", instructor_id).execute().data
        conflicts = []

        for lesson in lessons:
            if exclude_lesson_id and lesson.get("lesson_id") == exclude_lesson_id:
                continue

            if (_check_time_overlap(start_time, end_time, lesson.get("start_time"), lesson.get("end_time"))
                    and _recurrences_can_overlap(recurrence, lesson.get("recurrence"))):
                resource_name = _get_resource_name(lesson, "instructor")
                message = _format_conflict_message("instructor", resource_name, lesson.get("start_time"), lesson.get("end_time"))
                conflicts.append(message)

        return conflicts
    except Exception:
        return []


def _check_room_overlap(room_id, start_time, end_time, recurrence=None, exclude_lesson_id=None):
    """
    Check if room has overlapping lessons on the same schedule.
    Returns list of conflict messages, excluding current lesson if specified.
    """
    try:
        lessons = _db().table("lesson").select("*").eq("room_id", room_id).execute().data
        conflicts = []

        for lesson in lessons:
            if exclude_lesson_id and lesson.get("lesson_id") == exclude_lesson_id:
                continue

            if (_check_time_overlap(start_time, end_time, lesson.get("start_time"), lesson.get("end_time"))
                    and _recurrences_can_overlap(recurrence, lesson.get("recurrence"))):
                resource_name = _get_resource_name(lesson, "room")
                message = _format_conflict_message("room", resource_name, lesson.get("start_time"), lesson.get("end_time"))
                conflicts.append(message)

        return conflicts
    except Exception:
        return []


def _check_student_overlap(student_id, start_time, end_time, recurrence=None, exclude_lesson_id=None):
    """
    Check if student has overlapping lessons on the same schedule.
    Returns list of conflict messages, excluding current lesson if specified.
    """
    try:
        lessons = _db().table("lesson").select("*").contains("student_ids", [student_id]).execute().data
        conflicts = []

        for lesson in lessons:
            if exclude_lesson_id and lesson.get("lesson_id") == exclude_lesson_id:
                continue

            if (_check_time_overlap(start_time, end_time, lesson.get("start_time"), lesson.get("end_time"))
                    and _recurrences_can_overlap(recurrence, lesson.get("recurrence"))):
                resource_name = _get_resource_name(lesson, "student")
                message = _format_conflict_message("student", resource_name, lesson.get("start_time"), lesson.get("end_time"))
                conflicts.append(message)

        return conflicts
    except Exception:
        return []


def validate_lesson_overlaps(data, exclude_lesson_id=None):
    """
    Validate that lesson doesn't conflict with existing lessons.
    Returns (is_valid, error_message) tuple.
    """
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    instructor_id = data.get("instructor_id")
    room_id = data.get("room_id")
    recurrence = data.get("recurrence")
    student_ids = data.get("student_ids") or []

    if not all([start_time, end_time, instructor_id, room_id]):
        return False, "Missing required fields: start_time, end_time, instructor_id, room_id"

    instructor_conflicts = _check_instructor_overlap(instructor_id, start_time, end_time, recurrence, exclude_lesson_id)
    if instructor_conflicts:
        return False, instructor_conflicts[0]

    room_conflicts = _check_room_overlap(room_id, start_time, end_time, recurrence, exclude_lesson_id)
    if room_conflicts:
        return False, room_conflicts[0]

    for sid in student_ids:
        student_conflicts = _check_student_overlap(sid, start_time, end_time, recurrence, exclude_lesson_id)
        if student_conflicts:
            return False, student_conflicts[0]

    return True, None


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
    "status", "rate", "recurrence", "student_ids", "course_id", "capacity",
}


def _clean_payload(data: dict) -> dict:
    """Strip fields that don't map to lesson table columns."""
    return {k: v for k, v in data.items() if k in _LESSON_COLUMNS}


def create_lesson(data):
    is_valid, error_msg = validate_lesson_overlaps(data)
    if not is_valid:
        raise ConflictError(error_msg)
    return Lesson.create(_clean_payload(data))


def update_lesson(lesson_id, data):
    current = get_lesson_by_id(lesson_id)
    if not current:
        raise NotFoundError(f"Lesson {lesson_id} not found.")

    merged_data = {**current[0], **data}

    is_valid, error_msg = validate_lesson_overlaps(merged_data, exclude_lesson_id=lesson_id)
    if not is_valid:
        raise ConflictError(error_msg)

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
