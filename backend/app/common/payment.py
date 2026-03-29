from backend.app.domain.exceptions.exceptions import ConflictError, NotFoundError, ValidationError


class InvalidPaymentAmountError(ValidationError):
    """Raised when the payment amount is zero, negative, or otherwise invalid."""

    def __init__(self, message: str):
        super().__init__([{"field": "amount", "message": message}])


class InvoiceNotFoundError(NotFoundError):
    """Raised when the target invoice does not exist."""
    pass


class InvoiceCancelledError(ConflictError):
    """Raised when a payment is attempted against a cancelled invoice."""
    pass


class InvoiceAlreadyPaidError(ConflictError):
    """Raised when a payment is attempted against an already fully paid invoice."""
    pass


class OverpaymentError(ConflictError):
    """Raised when the payment amount exceeds the outstanding invoice balance."""
    pass
