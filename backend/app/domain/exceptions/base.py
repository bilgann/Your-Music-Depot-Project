"""
Base domain exceptions.

Use-case: raised by any domain service or entity when generic validation,
resource-not-found, or conflict conditions occur that are safe to surface
to the client as 4xx responses.
"""

from backend.app.common.errors import DomainError
from backend.app.domain.errors.base import (
    CONFLICT,
    NOT_FOUND,
    VALIDATION_FAILED,
    MESSAGES,
)


class ValidationError(DomainError):
    """Raised when data fails field-level validation.

    Use-case: a service or entity checks required fields or format constraints
    and collects all per-field failures before raising.

    Args:
        errors: list of dicts, e.g. [{"field": "email", "message": "Invalid format"}]
    """

    error_code = VALIDATION_FAILED

    def __init__(self, errors: list):
        self.errors = errors
        super().__init__(MESSAGES[VALIDATION_FAILED])


class NotFoundError(DomainError):
    """Raised when a requested resource does not exist.

    Use-case: a repository lookup returns no record for the given identifier.
    """

    error_code = NOT_FOUND

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[NOT_FOUND])


class ConflictError(DomainError):
    """Raised for business-rule violations, duplicates, or referential conflicts.

    Use-case: an operation would violate a domain invariant (e.g. double-booking,
    duplicate record, state-machine violation).
    """

    error_code = CONFLICT

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[CONFLICT])
