from backend.app.domain.services.payment import (
    compute_apply_amount,
    determine_invoice_status,
    validate_payment_request,
)
from backend.app.domain.exceptions.exceptions import (
    InvalidPaymentAmountError,
    InvoiceNotFoundError,
    NotFoundError,
)
from backend.app.infrastructure.database.repositories import Client
from backend.app.infrastructure.database.repositories import Invoice
from backend.app.infrastructure.database.repositories import Payment
from backend.app.infrastructure.database.repositories import Transaction
from backend.app.infrastructure.database.repositories.credit_transaction import CreditTransaction


# -- Basic CRUD -----------------------------------------------------------------

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


# -- Recording via invoice ------------------------------------------------------

def record_payment(data: dict) -> dict:
    """
    Validate and record a payment against a specific invoice, then update
    the invoice's amount_paid and status.
    """
    invoice_id = data.get("invoice_id")
    amount_raw = data.get("amount")

    if not invoice_id:
        raise InvalidPaymentAmountError("invoice_id is required.")

    try:
        amount = float(amount_raw)
    except (TypeError, ValueError):
        raise InvalidPaymentAmountError("amount must be a valid number.")

    if amount <= 0:
        raise InvalidPaymentAmountError("amount must be greater than 0.")

    rows = Invoice.get(invoice_id)
    if not rows:
        raise InvoiceNotFoundError("Invoice not found.")
    invoice = rows[0]

    validate_payment_request(invoice, amount)

    created_rows = Payment.create({
        "invoice_id": invoice_id,
        "amount": amount,
        "payment_method": data.get("payment_method", "Card"),
        "paid_on": data.get("paid_on"),
        "notes": data.get("notes", ""),
    })
    payment = created_rows[0] if created_rows else {}

    total = float(invoice.get("total_amount", 0))
    already_paid = float(invoice.get("amount_paid", 0))
    new_paid = already_paid + amount
    new_status = determine_invoice_status(total, new_paid, invoice["status"])
    Invoice.update(invoice_id, {"amount_paid": new_paid, "status": new_status})

    client_id = invoice.get("client_id")
    if client_id:
        recalculate_invoice_statuses(client_id)

    return payment


# -- Recording via client (credits wallet) --------------------------------------

def recalculate_invoice_statuses(client_id: str) -> None:
    """
    Recompute the status of every non-cancelled invoice for a client.

    Rules (applied in priority order):
      - amount_paid >= total_amount  → Paid
      - period_end is in the past    → Overdue
      - otherwise                    → Pending
    """
    from datetime import date
    today = date.today().isoformat()

    for inv in Invoice.get_by_client(client_id):
        if inv.get("status") == "Cancelled":
            continue
        total = float(inv.get("total_amount", 0))
        paid = float(inv.get("amount_paid", 0))

        if paid >= total:
            new_status = "Paid"
        elif (inv.get("period_end") or "") < today:
            new_status = "Overdue"
        else:
            new_status = "Pending"

        if new_status != inv.get("status"):
            Invoice.update(inv["invoice_id"], {"status": new_status})


def pay_via_client(client_id: str, amount: float, payment_method: str = "Card") -> dict:
    """
    Record a payment made by a client.

    Flow:
      1. Recalculate all invoice statuses so Overdue flags are current.
      2. Apply to Overdue invoices first (oldest first), then Pending.
      3. Any remainder is added to client.credits for future invoices.
      4. Recalculate statuses again so newly-paid invoices are marked Paid.
    """
    client_rows = Client.get(client_id)
    if not client_rows:
        raise NotFoundError("Client not found.")

    amount = round(float(amount), 2)
    if amount <= 0:
        raise InvalidPaymentAmountError("amount must be greater than 0.")

    # Ensure statuses are accurate before we decide which invoices to pay first.
    recalculate_invoice_statuses(client_id)

    Transaction.create(
        client_id, amount,
        f"Client payment received ({payment_method})",
        payment_method=payment_method,
    )

    remaining = amount
    applied = []

    # Fetch unpaid invoices already ordered by period_start; sort overdue first.
    unpaid = Client.get_unpaid_invoices(client_id)
    unpaid.sort(key=lambda inv: (0 if inv.get("status") == "Overdue" else 1, inv.get("period_start", "")))

    for invoice in unpaid:
        if remaining <= 0:
            break
        result = _apply_amount_to_invoice(client_id, invoice, remaining, payment_method)
        applied.append(result)
        remaining = round(remaining - result["applied"], 2)

    if remaining > 0:
        current_credits = float(client_rows[0].get("credits", 0))
        Client.update_credits(client_id, current_credits + remaining)
        CreditTransaction.create(client_id, remaining, "Added to credits - no outstanding invoices")

    # Reflect any status changes (e.g. Overdue → Paid) from this payment.
    recalculate_invoice_statuses(client_id)

    return {
        "invoices_applied": applied,
        "credits_added": remaining,
        "total_paid": amount,
    }


def try_apply_credits(client_id: str, invoice: dict) -> float:
    """
    Attempt to pay an invoice using the client's available credits.
    Called automatically after a new invoice is generated.
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
            client_id,
            -applied,
            f"Credits applied to invoice {invoice['invoice_id']}",
            invoice_id=invoice["invoice_id"],
        )

    return applied


# -- Internal helpers -----------------------------------------------------------

def _apply_amount_to_invoice(
    client_id: str, invoice: dict, amount: float, payment_method: str
) -> dict:
    """
    Apply up to amount to a single invoice using domain rules to determine
    how much can be applied and what the resulting status should be.

    Creates a Payment record and updates the invoice. Returns a summary dict.
    """
    apply_amount = compute_apply_amount(invoice, amount)
    if apply_amount <= 0:
        return {
            "invoice_id": invoice["invoice_id"],
            "applied": 0.0,
            "status": invoice["status"],
        }

    Payment.create({
        "invoice_id": invoice["invoice_id"],
        "amount": apply_amount,
        "payment_method": payment_method,
    })

    total = float(invoice.get("total_amount", 0))
    new_paid = round(float(invoice.get("amount_paid", 0)) + apply_amount, 2)
    new_status = determine_invoice_status(total, new_paid, invoice["status"])
    Invoice.update(invoice["invoice_id"], {"amount_paid": new_paid, "status": new_status})

    return {
        "invoice_id": invoice["invoice_id"],
        "applied": apply_amount,
        "status": new_status,
    }
