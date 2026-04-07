"""
Compatibility domain exceptions.

Use-case: raised by booking or assignment services when CompatibilityService
returns can_assign=False for a proposed instructor-student pairing.
"""

from backend.app.domain.errors.compatibility import (
    INSTRUCTOR_BLOCKED,
    INSTRUCTOR_REQUIREMENT_NOT_MET,
    INSTRUCTOR_RESTRICTION_VIOLATED,
    MESSAGES,
)
from backend.app.domain.exceptions.base import ConflictError


class InstructorBlockedError(ConflictError):
    """Raised when a hard BLOCKED pair override prevents the assignment.

    Use-case: booking service calls CompatibilityService.check() and receives
    a result with hard_verdict="blocked", then raises this to abort the booking.
    """

    error_code = INSTRUCTOR_BLOCKED

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[INSTRUCTOR_BLOCKED])


class InstructorRequirementNotMetError(ConflictError):
    """Raised when the instructor lacks a credential required by the student.

    Use-case: a student with a CPR or special-ed requirement is assigned to an
    instructor whose active credentials do not include that type.
    """

    error_code = INSTRUCTOR_REQUIREMENT_NOT_MET

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[INSTRUCTOR_REQUIREMENT_NOT_MET])


class InstructorRestrictionViolatedError(ConflictError):
    """Raised when the student does not meet the instructor's age or other restrictions.

    Use-case: an instructor with a min_student_age restriction is assigned to a
    student below that age threshold.
    """

    error_code = INSTRUCTOR_RESTRICTION_VIOLATED

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[INSTRUCTOR_RESTRICTION_VIOLATED])
