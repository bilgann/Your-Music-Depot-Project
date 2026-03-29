import calendar
from datetime import date

from backend.app.domain.invoice import build_line_items, compute_outstanding_balance
from backend.app.common.invoice import DuplicateInvoiceError, NoLessonsFoundError
from backend.app.infrastructure.models import AttendancePolicy
from backend.app.infrastructure.models import Invoice
from backend.app.infrastructure.models import Lesson
from backend.app.infrastructure.models import Student


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
    in the given calendar month.

    Charge calculation and line-item assembly are delegated to the domain layer.
    After creation, any available client credits are applied automatically.
    """
    period_start = date(year, month, 1).isoformat()
    last_day     = calendar.monthrange(year, month)[1]
    period_end   = date(year, month, last_day).isoformat()

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

    default_policy = AttendancePolicy.get_default()

    student_rows = Student.get(student_id)
    client_id    = student_rows[0].get("client_id") if student_rows else None

    line_items_data, total_amount = build_line_items(lessons, default_policy)

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
            "invoice_id":  invoice_id,
            "lesson_id":   item["lesson_id"],
            "description": item["description"],
            "amount":      item["amount"],
        }
        for item in line_items_data
    ])

    # Auto-apply client credits to the new invoice
    if client_id:
        from backend.app.application.services.payment import try_apply_credits
        try_apply_credits(client_id, invoice_row)
        updated = Invoice.get(invoice_id)
        if updated:
            invoice_row = updated[0]

    return {"invoice": invoice_row, "line_items": line_items_data}


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
