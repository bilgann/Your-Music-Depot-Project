# Backward-compatibility shim.
# These exceptions now live in domain.exceptions.financial.
from backend.app.domain.exceptions.financial import (
    InvalidPaymentAmountError,
    InvoiceAlreadyPaidError,
    InvoiceCancelledError,
    InvoiceNotFoundError,
    OverpaymentError,
)

__all__ = [
    "InvalidPaymentAmountError",
    "InvoiceNotFoundError",
    "InvoiceCancelledError",
    "InvoiceAlreadyPaidError",
    "OverpaymentError",
]
