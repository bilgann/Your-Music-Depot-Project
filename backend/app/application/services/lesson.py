from backend.app.domain.exceptions.exceptions import ConflictError, NotFoundError
from backend.app.infrastructure.database.database import DatabaseConnection
from backend.app.infrastructure.database.repositories import Lesson
from backend.app.infrastructure.database.repositories import LessonEnrollment


def _db():
    return DatabaseConnection().client


def _check_time_overlap(start1, end1, start2, end2):
    """
    Check if two time ranges overlap.
    Returns True if there's any overlap.
    """
    return start1 < end2 and end1 > start2


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


def _check_instructor_overlap(instructor_id, start_time, end_time, exclude_lesson_id=None):
    """
    Check if instructor has overlapping lessons.
    Returns list of conflict messages, excluding current lesson if specified.
    """
    try:
        lessons = _db().table("lesson").select("*").eq("instructor_id", instructor_id).execute().data
        conflicts = []
        
        for lesson in lessons:
            # Skip the current lesson if provided (for updates)
            if exclude_lesson_id and lesson.get("lesson_id") == exclude_lesson_id:
                continue
            
            # Check if times overlap
            if _check_time_overlap(start_time, end_time, lesson.get("start_time"), lesson.get("end_time")):
                resource_name = _get_resource_name(lesson, "instructor")
                message = _format_conflict_message("instructor", resource_name, lesson.get("start_time"), lesson.get("end_time"))
                conflicts.append(message)
        
        return conflicts
    except Exception:
        return []


def _check_room_overlap(room_id, start_time, end_time, exclude_lesson_id=None):
    """
    Check if room has overlapping lessons.
    Returns list of conflict messages, excluding current lesson if specified.
    """
    try:
        lessons = _db().table("lesson").select("*").eq("room_id", room_id).execute().data
        conflicts = []
        
        for lesson in lessons:
            # Skip the current lesson if provided (for updates)
            if exclude_lesson_id and lesson.get("lesson_id") == exclude_lesson_id:
                continue
            
            # Check if times overlap
            if _check_time_overlap(start_time, end_time, lesson.get("start_time"), lesson.get("end_time")):
                resource_name = _get_resource_name(lesson, "room")
                message = _format_conflict_message("room", resource_name, lesson.get("start_time"), lesson.get("end_time"))
                conflicts.append(message)
        
        return conflicts
    except Exception:
        return []


def _check_student_overlap(student_id, start_time, end_time, exclude_lesson_id=None):
    """
    Check if student has overlapping lessons.
    Returns list of conflict messages, excluding current lesson if specified.
    """
    try:
        lessons = _db().table("lesson").select("*").eq("student_id", student_id).execute().data
        conflicts = []
        
        for lesson in lessons:
            # Skip the current lesson if provided (for updates)
            if exclude_lesson_id and lesson.get("lesson_id") == exclude_lesson_id:
                continue
            
            # Check if times overlap
            if _check_time_overlap(start_time, end_time, lesson.get("start_time"), lesson.get("end_time")):
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
    Error message includes formatted conflict details.
    """
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    instructor_id = data.get("instructor_id")
    room_id = data.get("room_id")
    student_id = data.get("student_id")
    
    if not all([start_time, end_time, instructor_id, room_id, student_id]):
        return False, "Missing required fields: start_time, end_time, instructor_id, room_id, student_id"
    
    instrument = data.get("instrument")
    
    # Check if instrument is specified and validate instructor has the skill
    if instrument:
        has_skill, instructor_skill = _check_instructor_has_skill(instructor_id, instrument)
        if not has_skill:
            instructor_name = _get_instructor_name(instructor_id)
            return False, f"{instructor_name} is not certified to teach {instrument}"

        student_skill = _get_student_skill_record(student_id, instrument)
        if not student_skill:
            return False, f"Student {student_id} has no {instrument} skill level recorded"

        level_ok, instructor_min, student_level = _check_skill_level_match(instructor_skill, student_skill)
        if not level_ok:
            if instructor_min is None or student_level is None:
                return False, f"Missing skill levels for {instrument}: instructor min or student level is not set"
            return False, (
                f"Skill level mismatch for {instrument}: "
                f"instructor minimum is {instructor_min}, student level is {student_level}"
            )
    # Check instructor overlap
    instructor_conflicts = _check_instructor_overlap(instructor_id, start_time, end_time, exclude_lesson_id)
    if instructor_conflicts:
        # Return first instructor conflict message
        return False, instructor_conflicts[0]
    
    # Check room overlap
    room_conflicts = _check_room_overlap(room_id, start_time, end_time, exclude_lesson_id)
    if room_conflicts:
        # Return first room conflict message
        return False, room_conflicts[0]
    
    # Check student overlap
    student_conflicts = _check_student_overlap(student_id, start_time, end_time, exclude_lesson_id)
    if student_conflicts:
        # Return first student conflict message
        return False, student_conflicts[0]
    
    return True, None


def get_all_lessons():
    return Lesson.get_all()


def get_lessons_for_week(start, end):
    return Lesson.get_for_week(start, end)


def get_lesson_by_id(lesson_id):
    return Lesson.get(lesson_id)


def create_lesson(data):
    is_valid, error_msg = validate_lesson_overlaps(data)
    if not is_valid:
        raise ValueError(error_msg)
    return Lesson.create(data)


def update_lesson(lesson_id, data):
    # Get current lesson to merge with update data for validation
    current = get_lesson_by_id(lesson_id)
    if not current:
        raise ValueError(f"Lesson {lesson_id} not found")
    
    # Merge current data with update data for complete validation
    merged_data = {**current[0], **data}
    
    is_valid, error_msg = validate_lesson_overlaps(merged_data, exclude_lesson_id=lesson_id)
    if not is_valid:
        raise ValueError(error_msg)
    
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
