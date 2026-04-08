# Backward-compatibility shim.
# These exceptions now live in domain.exceptions.scheduling.
from backend.app.domain.exceptions.scheduling import InstructorUnavailableError, RoomUnavailableError

__all__ = ["InstructorUnavailableError", "RoomUnavailableError"]
