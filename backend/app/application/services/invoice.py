import calendar
from datetime import date

from backend.app.domain.services.invoice import build_line_items, compute_outstanding_balance
from backend.app.domain.exceptions.exceptions import DuplicateInvoiceError, NoLessonsFoundError
from backend.app.infrastructure.database.repositories import AttendancePolicy
from backend.app.infrastructure.database.repositories import Invoice
from backend.app.infrastructure.database.repositories import LessonOccurrence
from backend.app.infrastructure.database.repositories import Student


# ── Basic CRUD ────────────────────────────────────────────────────────────────

def get_all_invoices():
    return Invoice.get_all()


def get_invoice_by_id(invoice_id):
    return Invoice.get(invoice_id)


def get_invoices_by_client(client_id):
    return Invoice.get_by_client(client_id)


def create_invoice(data):
    return Invoice.create(data)


def update_invoice(invoice_id, data):
    return Invoice.update(invoice_id, data)


def delete_invoice(invoice_id):
    return Invoice.delete(invoice_id)


# ── Generation ────────────────────────────────────────────────────────────────

def generate_monthly_invoice(student_id, year: int, month: int) -> dict:
    """
    Generate an invoice for a student covering all Completed/Scheduled
    lesson occurrences in the given calendar month.

    Line items are built by the domain layer and now carry an item_type field.
    After creation, any available client credits are applied automatically.
    """
    period_start = date(year, month, 1).isoformat()
    last_day     = calendar.monthrange(year, month)[1]
    period_end   = date(year, month, last_day).isoformat()

    if Invoice.get_by_student_and_period(student_id, period_start):
        raise DuplicateInvoiceError(
            f"Invoice for student {student_id} covering {period_start} already exists."
        )

    occurrences = LessonOccurrence.get_for_student_in_period(
        student_id, period_start, period_end, ["Completed", "Scheduled"]
    )
    if not occurrences:
        raise NoLessonsFoundError(
            f"No Completed or Scheduled occurrences found for student {student_id} "
            f"in {year}-{month:02d}."
        )

    default_policy = AttendancePolicy.get_default()

    student_rows = Student.get(student_id)
    client_id    = student_rows[0].get("client_id") if student_rows else None

    line_items_data, total_amount = build_line_items(occurrences, default_policy)

    invoice_row = Invoice.create({
        "student_id":   student_id,
        "client_id":    client_id,
        "period_start": period_start,
        "period_end":   period_end,
        "total_amount": total_amount,
        "amount_paid":  0,
        "status":       "Pending",
    })[0]
    invoice_id = invoice_row["invoice_id"]

    Invoice.create_line_items([
        {
            "invoice_id":        invoice_id,
            "item_type":         item.get("item_type", "lesson"),
            "occurrence_id":     item.get("occurrence_id"),
            "description":       item["description"],
            "amount":            item["amount"],
            "attendance_status": item.get("attendance_status"),
        }
        for item in line_items_data
    ])

    if client_id:
        from backend.app.application.services.payment import try_apply_credits
        try_apply_credits(client_id, invoice_row)
        updated = Invoice.get(invoice_id)
        if updated:
            invoice_row = updated[0]

    return {"invoice": invoice_row, "line_items": line_items_data}


def add_invoice_item(invoice_id: str, data: dict) -> dict:
    """
    Add a non-lesson charge (instrument damage, purchase, etc.) to an existing invoice.
    Recalculates and persists the updated total_amount.
    """
    from backend.app.domain.exceptions.exceptions import NotFoundError
    rows = Invoice.get(invoice_id)
    if not rows:
        raise NotFoundError("Invoice not found.")

    item_row = Invoice.create_line_items([{
        "invoice_id":   invoice_id,
        "item_type":    data.get("item_type", "other"),
        "description":  data["description"],
        "amount":       data["amount"],
        "occurrence_id": data.get("occurrence_id"),
    }])

    # Recompute total from all items and persist the denormalised column.
    all_items  = Invoice.get_line_items(invoice_id)
    new_total  = sum(float(i.get("amount", 0)) for i in all_items)
    Invoice.update(invoice_id, {"total_amount": new_total})

    return item_row[0] if item_row else {}


# ── Line items ────────────────────────────────────────────────────────────────

def get_line_items(invoice_id) -> list:
    return Invoice.get_line_items(invoice_id)


# ── Outstanding balance ───────────────────────────────────────────────────────

def get_outstanding_balance(client_id=None) -> dict:
    pending = Invoice.get_pending()
    if client_id:
        pending = [inv for inv in pending if inv.get("client_id") == client_id]
    return {
        "invoices":                  pending,
        "total_outstanding_balance": compute_outstanding_balance(pending),
    }
