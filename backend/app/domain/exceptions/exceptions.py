"""
Backward-compatibility shim.

All exception classes have been split into subdomain modules:
  - domain.exceptions.base       — ValidationError, NotFoundError, ConflictError
  - domain.exceptions.financial  — invoice and payment exceptions
  - domain.exceptions.scheduling — InstructorUnavailableError, RoomUnavailableError

Import directly from those modules or from domain.exceptions (the package).
This shim re-exports everything so existing imports keep working.
"""

from backend.app.domain.exceptions.base import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from backend.app.domain.exceptions.financial import (
    DuplicateInvoiceError,
    InvalidPaymentAmountError,
    InvoiceAlreadyPaidError,
    InvoiceCancelledError,
    InvoiceNotFoundError,
    NoLessonsFoundError,
    OverpaymentError,
)
from backend.app.domain.exceptions.scheduling import (
    InstructorUnavailableError,
    RoomUnavailableError,
)
from backend.app.domain.exceptions.compatibility import (
    InstructorBlockedError,
    InstructorRequirementNotMetError,
    InstructorRestrictionViolatedError,
)

__all__ = [
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "DuplicateInvoiceError",
    "NoLessonsFoundError",
    "InvoiceNotFoundError",
    "InvoiceCancelledError",
    "InvoiceAlreadyPaidError",
    "OverpaymentError",
    "InvalidPaymentAmountError",
    "InstructorUnavailableError",
    "RoomUnavailableError",
    "InstructorBlockedError",
    "InstructorRequirementNotMetError",
    "InstructorRestrictionViolatedError",
]
