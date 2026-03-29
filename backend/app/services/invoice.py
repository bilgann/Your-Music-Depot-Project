import calendar
from datetime import date

from backend.app.exceptions.invoice import DuplicateInvoiceError, NoLessonsFoundError
from backend.app.models.invoice import Invoice
from backend.app.models.lesson import Lesson
from backend.app.models.student import Student
# Imported lazily inside generate_monthly_invoice to avoid circular imports
# from backend.app.services.payment import try_apply_credits


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
    Generate an invoice for a student covering all Completed/Scheduled lessons
    in the given calendar month. The invoice is billed to the student's client
    (if one exists). Creates one INVOICE row and one INVOICE_LINE row per lesson.
    """
    period_start = date(year, month, 1).isoformat()
    last_day = calendar.monthrange(year, month)[1]
    period_end = date(year, month, last_day).isoformat()

    if Invoice.get_by_student_and_period(student_id, period_start):
        raise DuplicateInvoiceError(
            f"Invoice for student {student_id} covering {period_start} already exists."
        )

    lessons = Lesson.get_for_student_in_period(
        student_id, period_start, period_end, ["Completed", "Scheduled"]
    )
    if not lessons:
        raise NoLessonsFoundError(
            f"No Completed or Scheduled lessons found for student {student_id} "
            f"in {year}-{month:02d}."
        )

    # Resolve the billing client from the student record
    student_rows = Student.get(student_id)
    client_id = student_rows[0].get("client_id") if student_rows else None

    total_amount = sum(float(lesson.get("rate", 0)) for lesson in lessons)

    invoice_row = Invoice.create({
        "student_id": student_id,
        "client_id": client_id,
        "period_start": period_start,
        "period_end": period_end,
        "total_amount": total_amount,
        "amount_paid": 0,
        "status": "Pending",
    })[0]
    invoice_id = invoice_row["invoice_id"]

    line_items = [
        {
            "invoice_id": invoice_id,
            "lesson_id": lesson["lesson_id"],
            "description": f"Lesson on {lesson['start_time'][:10]}",
            "amount": float(lesson.get("rate", 0)),
        }
        for lesson in lessons
    ]
    Invoice.create_line_items(line_items)

    # Auto-apply client credits to the new invoice
    if client_id:
        from backend.app.services.payment import try_apply_credits
        try_apply_credits(client_id, invoice_row)
        # Re-fetch so caller sees the updated amount_paid / status
        updated = Invoice.get(invoice_id)
        if updated:
            invoice_row = updated[0]

    return {"invoice": invoice_row, "line_items": line_items}


# ── Line items ────────────────────────────────────────────────────────────────

def get_line_items(invoice_id) -> list:
    return Invoice.get_line_items(invoice_id)


# ── Outstanding balance ───────────────────────────────────────────────────────

def get_outstanding_balance(client_id=None) -> dict:
    pending = Invoice.get_pending()
    if client_id:
        pending = [inv for inv in pending if inv.get("client_id") == client_id]
    total = sum(
        float(inv.get("total_amount", 0)) - float(inv.get("amount_paid", 0))
        for inv in pending
    )
    return {"invoices": pending, "total_outstanding_balance": total}
