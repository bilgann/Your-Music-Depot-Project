"""
Payment domain logic.

Pure functions encoding the business rules for applying payments to invoices
and managing the client credits wallet.

No database access.  Callers are responsible for all persistence.
"""

from __future__ import annotations

from backend.app.common.payment import (
    InvoiceAlreadyPaidError,
    InvoiceCancelledError,
    OverpaymentError,
)


# ── Invoice payment guards ────────────────────────────────────────────────────

def validate_payment_request(invoice: dict, amount: float) -> None:
    """
    Raise a domain exceptions if the payment request cannot be applied.

    Checks:
      - Invoice is not Cancelled
      - Invoice is not already fully Paid
      - amount does not exceed the outstanding balance
    """
    if invoice["status"] == "Cancelled":
        raise InvoiceCancelledError("Cannot pay a cancelled invoice.")
    if invoice["status"] == "Paid":
        raise InvoiceAlreadyPaidError("Invoice is already fully paid.")

    outstanding = _outstanding(invoice)
    if amount > outstanding:
        raise OverpaymentError(
            f"Payment of {amount} exceeds outstanding balance of {outstanding:.2f}."
        )


# ── Calculation helpers ───────────────────────────────────────────────────────

def compute_apply_amount(invoice: dict, requested: float) -> float:
    """
    Return the amount that should actually be applied to a single invoice.

    Caps the application at the invoice's outstanding balance so that a bulk
    client payment never over-pays a single invoice.
    """
    return round(min(requested, _outstanding(invoice)), 2)


def determine_invoice_status(total: float, new_paid: float, current_status: str) -> str:
    """
    Return the new invoice status after a payment is applied.

    Transitions to 'Paid' only when the full amount has been covered;
    otherwise retains the current status (typically 'Pending').
    """
    return "Paid" if new_paid >= total else current_status


# ── Internal ──────────────────────────────────────────────────────────────────

def _outstanding(invoice: dict) -> float:
    total       = float(invoice.get("total_amount", 0))
    already     = float(invoice.get("amount_paid",  0))
    return round(total - already, 2)
