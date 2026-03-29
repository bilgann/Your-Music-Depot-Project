"""
Scheduling domain rules.

Encapsulates the rule that a lesson cannot be created when the instructor
or room already has an overlapping booking.

Callers (services) are responsible for querying conflicts from the
repository; this layer only decides what to do with the results.
"""

from backend.app.domain.exceptions.exceptions import InstructorUnavailableError, RoomUnavailableError


def validate_no_instructor_conflict(conflicts: list) -> None:
    """Raise InstructorUnavailableError if any conflicting lessons are present."""
    if conflicts:
        raise InstructorUnavailableError("Instructor is not available during this time.")


def validate_no_room_conflict(conflicts: list) -> None:
    """Raise RoomUnavailableError if any conflicting lessons are present."""
    if conflicts:
        raise RoomUnavailableError("Room is not available during this time.")
