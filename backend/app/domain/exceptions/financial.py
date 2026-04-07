"""
Financial domain exceptions.

Use-case: raised by invoice-generation and payment-processing services when
business rules around billing are violated.
"""

from backend.app.domain.errors.financial import (
    DUPLICATE_INVOICE,
    INVALID_PAYMENT_AMOUNT,
    INVOICE_ALREADY_PAID,
    INVOICE_CANCELLED,
    INVOICE_NOT_FOUND,
    NO_LESSONS_FOUND,
    OVERPAYMENT,
    MESSAGES,
)
from backend.app.domain.exceptions.base import ConflictError, NotFoundError


class DuplicateInvoiceError(ConflictError):
    """Raised when an invoice for the same student and period already exists.

    Use-case: the invoice-generation service checks for an existing open invoice
    before creating a new one.
    """

    error_code = DUPLICATE_INVOICE

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[DUPLICATE_INVOICE])


class NoLessonsFoundError(NotFoundError):
    """Raised when no qualifying lessons exist for the requested invoice period.

    Use-case: invoice generation finds zero attended or scheduled lessons in the
    billing window and cannot produce a meaningful invoice.
    """

    error_code = NO_LESSONS_FOUND

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[NO_LESSONS_FOUND])


class InvoiceNotFoundError(NotFoundError):
    """Raised when the target invoice does not exist.

    Use-case: the payment service looks up an invoice by ID before recording
    a transaction.
    """

    error_code = INVOICE_NOT_FOUND

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[INVOICE_NOT_FOUND])


class InvoiceCancelledError(ConflictError):
    """Raised when attempting to pay a cancelled invoice.

    Use-case: the payment service checks invoice status before accepting a
    payment and rejects any operation on a cancelled invoice.
    """

    error_code = INVOICE_CANCELLED

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[INVOICE_CANCELLED])


class InvoiceAlreadyPaidError(ConflictError):
    """Raised when the invoice is already fully paid.

    Use-case: the payment service verifies outstanding balance is > 0 before
    processing a new transaction.
    """

    error_code = INVOICE_ALREADY_PAID

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[INVOICE_ALREADY_PAID])


class OverpaymentError(ConflictError):
    """Raised when the payment amount exceeds the outstanding balance.

    Use-case: the payment service compares the submitted amount against the
    invoice's outstanding balance and rejects overpayments.
    """

    error_code = OVERPAYMENT

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[OVERPAYMENT])


class InvalidPaymentAmountError(ConflictError):
    """Raised when the payment amount is zero or negative.

    Use-case: the payment service validates the submitted amount before any
    further processing.
    """

    error_code = INVALID_PAYMENT_AMOUNT

    def __init__(self, message: str = ""):
        super().__init__(message or MESSAGES[INVALID_PAYMENT_AMOUNT])
