from backend.app.exceptions.payment import (
    InvalidPaymentAmountError,
    InvoiceAlreadyPaidError,
    InvoiceCancelledError,
    InvoiceNotFoundError,
    OverpaymentError,
)
from backend.app.models.invoice import Invoice
from backend.app.models.payment import Payment


# ── Basic CRUD ────────────────────────────────────────────────────────────────

def get_all_payments():
    return Payment.get_all()


def get_payment_by_id(payment_id):
    return Payment.get(payment_id)


def delete_payment(payment_id):
    return Payment.delete(payment_id)


# ── Recording ─────────────────────────────────────────────────────────────────

def record_payment(data: dict) -> dict:
    """
    Validate and record a payment, then update the invoice's amount_paid.
    Sets invoice status to 'Paid' when the full balance is covered.
    """
    invoice_id = data.get("invoice_id")
    amount = data.get("amount")

    if not invoice_id:
        raise InvalidPaymentAmountError("invoice_id is required.")
    if amount is None or float(amount) <= 0:
        raise InvalidPaymentAmountError("amount must be greater than 0.")

    amount = float(amount)

    rows = Invoice.get(invoice_id)
    if not rows:
        raise InvoiceNotFoundError("Invoice not found.")
    invoice = rows[0]

    if invoice["status"] == "Cancelled":
        raise InvoiceCancelledError("Cannot pay a cancelled invoice.")
    if invoice["status"] == "Paid":
        raise InvoiceAlreadyPaidError("Invoice is already fully paid.")

    total = float(invoice.get("total_amount", 0))
    already_paid = float(invoice.get("amount_paid", 0))
    outstanding = total - already_paid

    if amount > outstanding:
        raise OverpaymentError(
            f"Payment of {amount} exceeds outstanding balance of {outstanding:.2f}."
        )

    payment = Payment.create({
        "invoice_id": invoice_id,
        "amount": amount,
        "payment_method": data.get("payment_method", "Card"),
        "paid_on": data.get("paid_on"),
        "notes": data.get("notes", ""),
    })[0]

    new_amount_paid = already_paid + amount
    new_status = "Paid" if new_amount_paid >= total else invoice["status"]
    Invoice.update(invoice_id, {"amount_paid": new_amount_paid, "status": new_status})

    return payment
