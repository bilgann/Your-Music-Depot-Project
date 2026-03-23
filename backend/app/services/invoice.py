import calendar
from datetime import date

from backend.app.singletons.database import DatabaseConnection


def _db():
    return DatabaseConnection().client


# ── Basic CRUD ────────────────────────────────────────────────────────────────

def get_all_invoices():
    return _db().table("invoice").select("*").execute().data


def get_invoice_by_id(invoice_id):
    return _db().table("invoice").select("*").eq("invoice_id", invoice_id).execute().data


def create_invoice(data):
    return _db().table("invoice").insert(data).execute().data


def update_invoice(invoice_id, data):
    return _db().table("invoice").update(data).eq("invoice_id", invoice_id).execute().data


def delete_invoice(invoice_id):
    return _db().table("invoice").delete().eq("invoice_id", invoice_id).execute().data


# ── Generation ────────────────────────────────────────────────────────────────

def generate_monthly_invoice(student_id, year: int, month: int) -> dict:
    """
    Generate an invoice for a student covering all Completed/Scheduled lessons
    in the given calendar month. Creates one INVOICE row and one INVOICE_LINE
    row per lesson. Raises ValueError if lessons are not found or an invoice for
    this student/period already exists.
    """
    period_start = date(year, month, 1).isoformat()
    last_day = calendar.monthrange(year, month)[1]
    period_end = date(year, month, last_day).isoformat()

    # Check for duplicate invoice
    existing = (
        _db()
        .table("invoice")
        .select("invoice_id")
        .eq("student_id", student_id)
        .eq("period_start", period_start)
        .execute()
        .data
    )
    if existing:
        raise ValueError(
            f"Invoice for student {student_id} covering {period_start} already exists."
        )

    # Fetch qualifying lessons
    lessons = (
        _db()
        .table("lesson")
        .select("*")
        .eq("student_id", student_id)
        .in_("status", ["Completed", "Scheduled"])
        .gte("start_time", period_start)
        .lte("start_time", period_end + "T23:59:59")
        .execute()
        .data
    )
    if not lessons:
        raise ValueError(
            f"No Completed or Scheduled lessons found for student {student_id} "
            f"in {year}-{month:02d}."
        )

    total_amount = sum(float(lesson.get("rate", 0)) for lesson in lessons)

    # Create invoice header
    invoice_row = (
        _db()
        .table("invoice")
        .insert(
            {
                "student_id": student_id,
                "period_start": period_start,
                "period_end": period_end,
                "total_amount": total_amount,
                "amount_paid": 0,
                "status": "Pending",
            }
        )
        .execute()
        .data[0]
    )
    invoice_id = invoice_row["invoice_id"]

    # Create one line per lesson
    line_items = [
        {
            "invoice_id": invoice_id,
            "lesson_id": lesson["lesson_id"],
            "description": f"Lesson on {lesson['start_time'][:10]}",
            "amount": float(lesson.get("rate", 0)),
        }
        for lesson in lessons
    ]
    _db().table("invoice_line").insert(line_items).execute()

    return {"invoice": invoice_row, "line_items": line_items}


# ── Line items ────────────────────────────────────────────────────────────────

def get_line_items(invoice_id) -> list:
    return (
        _db()
        .table("invoice_line")
        .select("*")
        .eq("invoice_id", invoice_id)
        .execute()
        .data
    )


# ── Outstanding balance ───────────────────────────────────────────────────────

def get_outstanding_balance() -> dict:
    pending = (
        _db()
        .table("invoice")
        .select("*")
        .eq("status", "Pending")
        .execute()
        .data
    )
    total = sum(
        float(inv.get("total_amount", 0)) - float(inv.get("amount_paid", 0))
        for inv in pending
    )
    return {"invoices": pending, "total_outstanding_balance": total}