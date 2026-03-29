import calendar
from datetime import date

from backend.app.exceptions.invoice import DuplicateInvoiceError, NoLessonsFoundError
from backend.app.models.invoice import Invoice
from backend.app.models.lesson import Lesson


# ── Basic CRUD ────────────────────────────────────────────────────────────────

def get_all_invoices():
    return Invoice.get_all()


def get_invoice_by_id(invoice_id):
    return Invoice.get(invoice_id)


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
    in the given calendar month. Creates one INVOICE row and one INVOICE_LINE
    row per lesson. Raises an error if lessons are not found or an invoice for
    this student/period already exists.
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

    total_amount = sum(float(lesson.get("rate", 0)) for lesson in lessons)

    invoice_row = Invoice.create({
        "student_id": student_id,
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

    return {"invoice": invoice_row, "line_items": line_items}


# ── Line items ────────────────────────────────────────────────────────────────

def get_line_items(invoice_id) -> list:
    return Invoice.get_line_items(invoice_id)


# ── Outstanding balance ───────────────────────────────────────────────────────

def get_outstanding_balance() -> dict:
    pending = Invoice.get_pending()
    total = sum(
        float(inv.get("total_amount", 0)) - float(inv.get("amount_paid", 0))
        for inv in pending
    )
    return {"invoices": pending, "total_outstanding_balance": total}
