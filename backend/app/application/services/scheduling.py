from backend.app.domain.scheduling import validate_no_instructor_conflict, validate_no_room_conflict
from backend.app.infrastructure.models import Lesson
from backend.app.infrastructure.models import Schedule


def create_lesson(data):
    """
    Create a new lesson after verifying that neither the instructor nor the
    room has a conflicting booking in the requested time window.

    Conflict queries are handled by the repository (Schedule model); the
    domain layer decides whether those conflicts should block creation.
    """
    instructor_conflicts = Schedule.get_instructor_conflicts(
        data["instructor_id"], data["start_time"], data["end_time"]
    )
    validate_no_instructor_conflict(instructor_conflicts)

    room_conflicts = Schedule.get_room_conflicts(
        data["room_id"], data["start_time"], data["end_time"]
    )
    validate_no_room_conflict(room_conflicts)

    return Lesson.create(data)
