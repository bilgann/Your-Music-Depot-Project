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

__all__ = [
    # base
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    # financial
    "DuplicateInvoiceError",
    "NoLessonsFoundError",
    "InvoiceNotFoundError",
    "InvoiceCancelledError",
    "InvoiceAlreadyPaidError",
    "OverpaymentError",
    "InvalidPaymentAmountError",
    # scheduling
    "InstructorUnavailableError",
    "RoomUnavailableError",
]
