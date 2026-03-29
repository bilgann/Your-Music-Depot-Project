from backend.app.exceptions.base import ConflictError


class InstructorUnavailableError(ConflictError):
    """Raised when the instructor already has a booking during the requested time."""
    pass


class RoomUnavailableError(ConflictError):
    """Raised when the room is already occupied during the requested time."""
    pass
