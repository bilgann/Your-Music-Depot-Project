import calendar
from datetime import date

from backend.app.exceptions.invoice import DuplicateInvoiceError, NoLessonsFoundError
from backend.app.models.attendance_policy import AttendancePolicy
from backend.app.models.invoice import Invoice
from backend.app.models.lesson import Lesson
from backend.app.models.student import Student


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


# ── Attendance-based charge calculation ───────────────────────────────────────

def _apply_policy_rule(rate: float, charge_type: str, charge_value: float) -> float:
    if charge_type == "flat":
        return round(float(charge_value), 2)
    if charge_type == "percentage":
        return round(rate * float(charge_value) / 100, 2)
    return 0.0  # "none"


def _calculate_charge(lesson: dict, default_policy: dict | None) -> float:
    """
    Return the charge for a single lesson based on the student's attendance.

    Attendance status → charge rule:
      Present / null (not yet recorded) → full rate
      Excused                           → $0
      Absent                            → absent_charge rule from policy
      Late Cancel                       → late_cancel_charge rule from policy
    """
    rate = float(lesson.get("rate") or 0)
    status = lesson.get("attendance_status")

    if status == "Excused":
        return 0.0
    if status in ("Absent", "Cancelled", "Late Cancel"):
        policy = lesson.get("attendance_policy") or default_policy
        if not policy:
            return rate  # no policy configured → charge in full
        key = {"Absent": "absent", "Cancelled": "cancel", "Late Cancel": "late_cancel"}[status]
        return _apply_policy_rule(
            rate,
            policy.get(f"{key}_charge_type", "none"),
            policy.get(f"{key}_charge_value", 0),
        )

    return rate  # Present or unrecorded → full rate


def _attendance_label(status: str | None) -> str:
    return {
        "Present": "Present",
        "Absent": "Absent",
        "Cancelled": "Cancelled",
        "Late Cancel": "Late cancellation",
        "Excused": "Excused",
        None: "Attended",
    }.get(status, status or "Attended")


# ── Generation ────────────────────────────────────────────────────────────────

def generate_monthly_invoice(student_id, year: int, month: int) -> dict:
    """
    Generate an invoice for a student covering all Completed/Scheduled lessons
    in the given calendar month.

    Each lesson is charged according to the student's attendance status and the
    lesson's attendance policy (falling back to the school-wide default policy).
    Excused absences are $0; regular absences and late cancellations follow the
    configured charge rules.
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

    default_policy = AttendancePolicy.get_default()

    # Resolve billing client from student record
    student_rows = Student.get(student_id)
    client_id = student_rows[0].get("client_id") if student_rows else None

    line_items_data = []
    total_amount = 0.0

    for lesson in lessons:
        charge = _calculate_charge(lesson, default_policy)
        label = _attendance_label(lesson.get("attendance_status"))
        line_items_data.append({
            "lesson_id": lesson["lesson_id"],
            "description": f"{label} — {lesson['start_time'][:10]}",
            "amount": charge,
            "attendance_status": lesson.get("attendance_status"),
        })
        total_amount += charge

    total_amount = round(total_amount, 2)

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

    db_line_items = [
        {
            "invoice_id": invoice_id,
            "lesson_id": item["lesson_id"],
            "description": item["description"],
            "amount": item["amount"],
        }
        for item in line_items_data
    ]
    Invoice.create_line_items(db_line_items)

    # Auto-apply client credits to the new invoice
    if client_id:
        from backend.app.services.payment import try_apply_credits
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
    total = sum(
        float(inv.get("total_amount", 0)) - float(inv.get("amount_paid", 0))
        for inv in pending
    )
    return {"invoices": pending, "total_outstanding_balance": total}
