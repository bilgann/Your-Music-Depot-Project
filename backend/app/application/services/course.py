import uuid

from backend.app.domain.exceptions.exceptions import ConflictError, NotFoundError
from backend.app.domain.services import schedule_projection
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
from backend.app.infrastructure.database.repositories import (
    Course,
    Instructor,
    LessonEnrollment,
    LessonOccurrence,
    Room,
    Student,
)


# ── CRUD ──────────────────────────────────────────────────────────────────────

def get_all_courses():
    return Course.get_all()


def get_course_by_id(course_id):
    return Course.get(course_id)


def get_courses_by_instructor(instructor_id):
    return Course.get_by_instructor(instructor_id)


def get_courses_by_student(student_id):
    return Course.get_by_student(student_id)


def create_course(data):
    return Course.create(data)


def update_course(course_id, data):
    rows = Course.get(course_id)
    if not rows:
        raise NotFoundError("Course not found.")
    return Course.update(course_id, data)


def delete_course(course_id):
    rows = Course.get(course_id)
    if not rows:
        raise NotFoundError("Course not found.")
    # Remove projected occurrences and their enrollments before deleting.
    for occ in LessonOccurrence.get_by_course(course_id):
        LessonEnrollment.delete_by_occurrence(occ["occurrence_id"])
    LessonOccurrence.delete_by_course(course_id)
    return Course.delete(course_id)


# ── Roster management ─────────────────────────────────────────────────────────

def enroll_student(course_id, student_id):
    rows = Course.get(course_id)
    if not rows:
        raise NotFoundError("Course not found.")
    course = rows[0]
    student_ids = list(course.get("student_ids") or [])
    if student_id in student_ids:
        raise ConflictError("Student is already enrolled in this course.")
    student_ids.append(student_id)
    return Course.update(course_id, {"student_ids": student_ids})


def unenroll_student(course_id, student_id):
    rows = Course.get(course_id)
    if not rows:
        raise NotFoundError("Course not found.")
    course = rows[0]
    student_ids = list(course.get("student_ids") or [])
    if student_id not in student_ids:
        raise NotFoundError("Student is not enrolled in this course.")
    student_ids.remove(student_id)
    return Course.update(course_id, {"student_ids": student_ids})


def add_instructor(course_id, instructor_id):
    rows = Course.get(course_id)
    if not rows:
        raise NotFoundError("Course not found.")
    course = rows[0]
    instructor_ids = list(course.get("instructor_ids") or [])
    if instructor_id in instructor_ids:
        raise ConflictError("Instructor is already assigned to this course.")
    instructor_ids.append(instructor_id)
    return Course.update(course_id, {"instructor_ids": instructor_ids})


def remove_instructor(course_id, instructor_id):
    rows = Course.get(course_id)
    if not rows:
        raise NotFoundError("Course not found.")
    course = rows[0]
    instructor_ids = list(course.get("instructor_ids") or [])
    if instructor_id not in instructor_ids:
        raise NotFoundError("Instructor is not assigned to this course.")
    if len(instructor_ids) == 1:
        raise ConflictError("Cannot remove the last instructor from a course.")
    instructor_ids.remove(instructor_id)
    return Course.update(course_id, {"instructor_ids": instructor_ids})


# ── Schedule projection ───────────────────────────────────────────────────────

def project_course_schedule(course_id: str) -> list:
    """
    Expand the course's recurrence rule into LessonOccurrenceEntity stubs,
    collect blocked_times from all participants, and persist the result.

    Any previously projected occurrences (and their enrollments) are deleted
    first so projection is idempotent.
    """
    from backend.app.domain.entities.course import CourseEntity
    from backend.app.domain.entities.instructor import InstructorEntity
    from backend.app.domain.entities.room import RoomEntity
    from backend.app.domain.entities.client import ClientEntity

    rows = Course.get(course_id)
    if not rows:
        raise NotFoundError("Course not found.")

    course = CourseEntity.from_dict(rows[0])

    # Collect blocked times from all participants.
    blocked: list[BlockedTime] = []

    # School-wide blocked times (holidays, vacations) — filtered by overrides.
    from backend.app.application.services.school_schedule import collect_school_blocked_times
    override_checks: list[tuple[str, str]] = [
        ("course", course.course_id),
        ("room", course.room_id),
    ]
    for iid in course.instructor_ids:
        override_checks.append(("instructor", iid))
    blocked.extend(collect_school_blocked_times(override_checks))

    for iid in course.instructor_ids:
        irows = Instructor.get(iid)
        if irows:
            entity = InstructorEntity.from_dict(irows[0])
            blocked.extend(entity.blocked_times)

    rrows = Room.get(course.room_id)
    if rrows:
        entity = RoomEntity.from_dict(rrows[0])
        blocked.extend(entity.blocked_times)

    for sid in course.student_ids:
        srows = Student.get(sid)
        if srows and srows[0].get("client_id"):
            from backend.app.infrastructure.database.repositories import Client
            crows = Client.get(srows[0]["client_id"])
            if crows:
                entity = ClientEntity.from_dict(crows[0])
                blocked.extend(entity.blocked_times)

    # Re-project: delete existing occurrences first.
    for occ in LessonOccurrence.get_by_course(course_id):
        LessonEnrollment.delete_by_occurrence(occ["occurrence_id"])
    LessonOccurrence.delete_by_course(course_id)

    occurrence_stubs = schedule_projection.project_course_occurrences(course, blocked)

    if not occurrence_stubs:
        return []

    rows_to_insert = []
    for stub in occurrence_stubs:
        d = stub.to_dict()
        d["occurrence_id"] = str(uuid.uuid4())
        rows_to_insert.append(d)

    saved = LessonOccurrence.bulk_create(rows_to_insert)

    # Auto-enroll course students into every new occurrence.
    if course.student_ids and saved:
        enrollments = [
            {"occurrence_id": occ["occurrence_id"], "student_id": sid}
            for occ in saved
            for sid in course.student_ids
        ]
        for enr in enrollments:
            LessonEnrollment.create(enr["occurrence_id"], enr["student_id"])

    return saved
