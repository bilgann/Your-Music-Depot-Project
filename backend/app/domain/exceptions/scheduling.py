"""
Scheduling domain exceptions.

Use-case: raised by scheduling services when instructor or room availability
conflicts prevent a lesson from being booked or projected.
"""

from backend.app.domain.errors.scheduling import (
    INSTRUCTOR_UNAVAILABLE,
    ROOM_UNAVAILABLE,
    MESSAGES,
)
from backend.app.domain.exceptions.base import ConflictError


class InstructorUnavailableError(ConflictError):
    """Raised when the instructor has a blocked time or conflicting lesson.

    Use-case: the schedule-projection or booking service checks the instructor's
    blocked_times and existing occurrences before creating a new occurrence.
    """

    error_code = INSTRUCTOR_UNAVAILABLE

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[INSTRUCTOR_UNAVAILABLE])


class RoomUnavailableError(ConflictError):
    """Raised when the room has a blocked time or conflicting booking.

    Use-case: the schedule-projection or booking service checks the room's
    blocked_times and existing occurrences before assigning the room.
    """

    error_code = ROOM_UNAVAILABLE

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[ROOM_UNAVAILABLE])
