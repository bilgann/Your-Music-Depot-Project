from backend.app.domain.services.payment import (
    compute_apply_amount,
    determine_invoice_status,
    validate_payment_request,
)
from backend.app.domain.exceptions.exceptions import NotFoundError
from backend.app.domain.exceptions.exceptions import InvalidPaymentAmountError, InvoiceNotFoundError
from backend.app.infrastructure.database.repositories import Client
from backend.app.infrastructure.database.repositories.credit_transaction import CreditTransaction
from backend.app.infrastructure.database.repositories import Invoice
from backend.app.infrastructure.database.repositories import Payment


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
    Validate and record a payment against a specific invoice, then update
    the invoice's amount_paid and status.

    Domain rules (guard conditions, overpayment check) are enforced by the
    domain layer before any writes occur.
    """
    invoice_id = data.get("invoice_id")
    amount     = data.get("amount")

    if not invoice_id:
        raise InvalidPaymentAmountError("invoice_id is required.")
    if amount is None or float(amount) <= 0:
        raise InvalidPaymentAmountError("amount must be greater than 0.")

    amount = float(amount)

    rows = Invoice.get(invoice_id)
    if not rows:
        raise InvoiceNotFoundError("Invoice not found.")
    invoice = rows[0]

    validate_payment_request(invoice, amount)

    payment = Payment.create({
        "invoice_id":     invoice_id,
        "amount":         amount,
        "payment_method": data.get("payment_method", "Card"),
        "paid_on":        data.get("paid_on"),
        "notes":          data.get("notes", ""),
    })[0]

    total        = float(invoice.get("total_amount", 0))
    already_paid = float(invoice.get("amount_paid", 0))
    new_paid     = already_paid + amount
    new_status   = determine_invoice_status(total, new_paid, invoice["status"])
    Invoice.update(invoice_id, {"amount_paid": new_paid, "status": new_status})

    return payment


# ── Recording via client (credits wallet) ────────────────────────────────────

def pay_via_client(client_id: str, amount: float, payment_method: str = "Card") -> dict:
    """
    Record a payment made by a client.

    Flow:
      1. Apply the incoming amount to the client's oldest Pending invoices first.
      2. Any remainder is added to client.credits for future invoices.

    Returns a summary: invoices_applied, credits_added, total_paid.
    """
    client_rows = Client.get(client_id)
    if not client_rows:
        raise NotFoundError("Client not found.")

    amount = round(float(amount), 2)
    if amount <= 0:
        raise InvalidPaymentAmountError("amount must be greater than 0.")

    CreditTransaction.create(client_id, amount, f"Client payment received ({payment_method})")

    remaining = amount
    applied   = []

    for invoice in Client.get_pending_invoices(client_id):
        if remaining <= 0:
            break
        result     = _apply_amount_to_invoice(client_id, invoice, remaining, payment_method)
        applied.append(result)
        remaining  = round(remaining - result["applied"], 2)

    if remaining > 0:
        current_credits = float(client_rows[0].get("credits", 0))
        Client.update_credits(client_id, current_credits + remaining)
        CreditTransaction.create(client_id, remaining, "Added to credits \u2014 no outstanding invoices")

    return {
        "invoices_applied": applied,
        "credits_added":    remaining,
        "total_paid":       amount,
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

    result  = _apply_amount_to_invoice(client_id, invoice, credits, "Credits")
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

def _apply_amount_to_invoice(
    client_id: str, invoice: dict, amount: float, payment_method: str
) -> dict:
    """
    Apply up to `amount` to a single invoice using domain rules to determine
    how much can be applied and what the resulting status should be.

    Creates a Payment record and updates the invoice.  Returns a summary dict.
    """
    apply = compute_apply_amount(invoice, amount)
    if apply <= 0:
        return {"invoice_id": invoice["invoice_id"], "applied": 0.0, "status": invoice["status"]}

    Payment.create({
        "invoice_id":     invoice["invoice_id"],
        "amount":         apply,
        "payment_method": payment_method,
    })

    total      = float(invoice.get("total_amount", 0))
    new_paid   = round(float(invoice.get("amount_paid", 0)) + apply, 2)
    new_status = determine_invoice_status(total, new_paid, invoice["status"])
    Invoice.update(invoice["invoice_id"], {"amount_paid": new_paid, "status": new_status})

    return {"invoice_id": invoice["invoice_id"], "applied": apply, "status": new_status}
