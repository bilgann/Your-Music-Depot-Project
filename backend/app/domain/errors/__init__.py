from backend.app.domain.errors.base import (
    CONFLICT,
    NOT_FOUND,
    VALIDATION_FAILED,
    MESSAGES as BASE_MESSAGES,
)
from backend.app.domain.errors.financial import (
    DUPLICATE_INVOICE,
    INVALID_PAYMENT_AMOUNT,
    INVOICE_ALREADY_PAID,
    INVOICE_CANCELLED,
    INVOICE_NOT_FOUND,
    NO_LESSONS_FOUND,
    OVERPAYMENT,
    MESSAGES as FINANCIAL_MESSAGES,
)
from backend.app.domain.errors.scheduling import (
    INSTRUCTOR_UNAVAILABLE,
    ROOM_UNAVAILABLE,
    MESSAGES as SCHEDULING_MESSAGES,
)
from backend.app.domain.errors.compatibility import (
    INSTRUCTOR_BLOCKED,
    INSTRUCTOR_REQUIREMENT_NOT_MET,
    INSTRUCTOR_RESTRICTION_VIOLATED,
    MESSAGES as COMPATIBILITY_MESSAGES,
)

# Combined message lookup — merge all subdomain message dicts.
MESSAGES: dict[str, str] = {
    **BASE_MESSAGES,
    **FINANCIAL_MESSAGES,
    **SCHEDULING_MESSAGES,
    **COMPATIBILITY_MESSAGES,
}

__all__ = [
    # codes — base
    "VALIDATION_FAILED",
    "NOT_FOUND",
    "CONFLICT",
    # codes — financial
    "DUPLICATE_INVOICE",
    "NO_LESSONS_FOUND",
    "INVOICE_NOT_FOUND",
    "INVOICE_CANCELLED",
    "INVOICE_ALREADY_PAID",
    "OVERPAYMENT",
    "INVALID_PAYMENT_AMOUNT",
    # codes — scheduling
    "INSTRUCTOR_UNAVAILABLE",
    "ROOM_UNAVAILABLE",
    # codes — compatibility
    "INSTRUCTOR_BLOCKED",
    "INSTRUCTOR_REQUIREMENT_NOT_MET",
    "INSTRUCTOR_RESTRICTION_VIOLATED",
    # combined lookup
    "MESSAGES",
]
