from backend.app.exceptions.payment import (
    InvalidPaymentAmountError,
    InvoiceAlreadyPaidError,
    InvoiceCancelledError,
    InvoiceNotFoundError,
    OverpaymentError,
)
from backend.app.exceptions.base import NotFoundError
from backend.app.models.client import Client
from backend.app.models.credit_transaction import CreditTransaction
from backend.app.models.invoice import Invoice
from backend.app.models.payment import Payment


# ── Basic CRUD ────────────────────────────────────────────────────────────────

def get_all_payments():
    return Payment.get_all()


def list_payments(page: int = 1, page_size: int = 20):
    return Payment.list(page, page_size)


def get_payment_by_id(payment_id):
    return Payment.get(payment_id)


def get_payments_by_client(client_id):
    return Payment.get_by_client(client_id)


def delete_payment(payment_id):
    return Payment.delete(payment_id)


# ── Recording via invoice ─────────────────────────────────────────────────────

def record_payment(data: dict) -> dict:
    """
    Validate and record a payment against a specific invoice,
    then update the invoice's amount_paid and status.
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


# ── Recording via client (credits wallet) ────────────────────────────────────

def pay_via_client(client_id: str, amount: float, payment_method: str = "Card") -> dict:
    """
    Record a payment made by a client.

    Flow:
      1. Apply the incoming amount to the client's oldest Pending invoices first.
      2. Any remainder is added to client.credits for future invoices.

    Returns a summary: invoices paid, invoices partially paid, and credits added.
    """
    client_rows = Client.get(client_id)
    if not client_rows:
        raise NotFoundError("Client not found.")

    amount = round(float(amount), 2)
    if amount <= 0:
        raise InvalidPaymentAmountError("amount must be greater than 0.")

    # Log the incoming client payment
    CreditTransaction.create(client_id, amount, f"Client payment received ({payment_method})")

    remaining = amount
    applied = []

    pending_invoices = Client.get_pending_invoices(client_id)
    for invoice in pending_invoices:
        if remaining <= 0:
            break
        result = _apply_amount_to_invoice(client_id, invoice, remaining, payment_method)
        applied.append(result)
        remaining = round(remaining - result["applied"], 2)

    # Remainder → credits
    if remaining > 0:
        current_credits = float(client_rows[0].get("credits", 0))
        Client.update_credits(client_id, current_credits + remaining)
        CreditTransaction.create(client_id, remaining, "Added to credits — no outstanding invoices")

    return {
        "invoices_applied": applied,
        "credits_added": remaining,
        "total_paid": amount,
    }


def try_apply_credits(client_id: str, invoice: dict) -> float:
    """
    Attempt to pay an invoice using the client's available credits.
    Called automatically when a new invoice is generated.
    Returns the amount applied from credits.
    """
    client_rows = Client.get(client_id)
    if not client_rows:
        return 0.0

    credits = round(float(client_rows[0].get("credits", 0)), 2)
    if credits <= 0:
        return 0.0

    result = _apply_amount_to_invoice(client_id, invoice, credits, "Credits")
    applied = result["applied"]

    if applied > 0:
        new_credits = round(credits - applied, 2)
        Client.update_credits(client_id, new_credits)
        CreditTransaction.create(
            client_id, -applied,
            f"Credits applied to invoice {invoice['invoice_id']}",
            invoice["invoice_id"],
        )

    return applied


# ── Internal helpers ──────────────────────────────────────────────────────────

def _apply_amount_to_invoice(client_id: str, invoice: dict, amount: float, payment_method: str) -> dict:
    """
    Apply up to `amount` to a single invoice. Creates a Payment record and
    updates the invoice. Returns {"invoice_id", "applied", "status"}.
    """
    total = float(invoice.get("total_amount", 0))
    already_paid = float(invoice.get("amount_paid", 0))
    outstanding = round(total - already_paid, 2)

    apply = round(min(amount, outstanding), 2)
    if apply <= 0:
        return {"invoice_id": invoice["invoice_id"], "applied": 0.0, "status": invoice["status"]}

    Payment.create({
        "invoice_id": invoice["invoice_id"],
        "amount": apply,
        "payment_method": payment_method,
    })

    new_paid = round(already_paid + apply, 2)
    new_status = "Paid" if new_paid >= total else invoice["status"]
    Invoice.update(invoice["invoice_id"], {"amount_paid": new_paid, "status": new_status})

    return {"invoice_id": invoice["invoice_id"], "applied": apply, "status": new_status}
