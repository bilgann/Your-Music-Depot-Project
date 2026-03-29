"""
Invoice domain logic.

Pure functions for:
  - Mapping attendance status to human-readable labels
  - Calculating per-lesson charges based on attendance and policy
  - Building line-item collections from a lesson list
  - Computing outstanding balance across a set of invoices

No database access.  Callers are responsible for fetching lessons,
policies, and invoices from the repository layer.
"""

from __future__ import annotations

# ── Attendance label mapping ──────────────────────────────────────────────────

_ATTENDANCE_LABELS: dict[str | None, str] = {
    "Present":     "Present",
    "Absent":      "Absent",
    "Cancelled":   "Cancelled",
    "Late Cancel": "Late cancellation",
    "Excused":     "Excused",
    None:          "Attended",
}

# Maps attendance status → policy key prefix used in attendance_policy rows
_ABSENCE_POLICY_KEY: dict[str, str] = {
    "Absent":      "absent",
    "Cancelled":   "cancel",
    "Late Cancel": "late_cancel",
}


def attendance_label(status: str | None) -> str:
    """Return a display-friendly label for an attendance status value."""
    return _ATTENDANCE_LABELS.get(status, status or "Attended")


# ── Charge calculation ────────────────────────────────────────────────────────

def apply_policy_rule(rate: float, charge_type: str, charge_value: float) -> float:
    """
    Apply a single charge rule (none / flat / percentage) to a lesson rate.

      none       → $0
      flat       → charge_value (regardless of rate)
      percentage → rate × charge_value / 100
    """
    if charge_type == "flat":
        return round(float(charge_value), 2)
    if charge_type == "percentage":
        return round(rate * float(charge_value) / 100, 2)
    return 0.0  # "none"


def calculate_lesson_charge(lesson: dict, default_policy: dict | None) -> float:
    """
    Return the charge for a single lesson based on the student's attendance status
    and the applicable attendance policy.

    Rules:
      Present / null (not yet recorded) → full lesson rate
      Excused                           → $0
      Absent / Cancelled / Late Cancel  → apply policy rule (absent / cancel /
                                          late_cancel charge type + value)

    The lesson-level policy takes priority; if absent, falls back to
    default_policy.  If neither exists, charges the full rate.
    """
    rate = float(lesson.get("rate") or 0)
    status = lesson.get("attendance_status")

    if status == "Excused":
        return 0.0

    if status in _ABSENCE_POLICY_KEY:
        policy = lesson.get("attendance_policy") or default_policy
        if not policy:
            return rate  # no policy configured — charge in full
        key = _ABSENCE_POLICY_KEY[status]
        return apply_policy_rule(
            rate,
            policy.get(f"{key}_charge_type", "none"),
            policy.get(f"{key}_charge_value", 0),
        )

    return rate  # Present or unrecorded → full rate


# ── Line-item building ────────────────────────────────────────────────────────

def build_line_items(
    lessons: list[dict],
    default_policy: dict | None,
) -> tuple[list[dict], float]:
    """
    Compute line-item data and the total invoice amount for a list of lessons.

    Returns:
        (line_items, total_amount) where line_items is a list of dicts ready
        to be inserted into invoice_line, and total_amount is pre-rounded.
    """
    line_items: list[dict] = []
    total = 0.0

    for lesson in lessons:
        charge = calculate_lesson_charge(lesson, default_policy)
        label  = attendance_label(lesson.get("attendance_status"))
        line_items.append({
            "lesson_id":         lesson["lesson_id"],
            "description":       f"{label} \u2014 {lesson['start_time'][:10]}",
            "amount":            charge,
            "attendance_status": lesson.get("attendance_status"),
        })
        total += charge

    return line_items, round(total, 2)


# ── Balance calculation ───────────────────────────────────────────────────────

def compute_outstanding_balance(invoices: list[dict]) -> float:
    """Return the total outstanding (unpaid) amount across a list of invoices."""
    return round(
        sum(
            float(inv.get("total_amount", 0)) - float(inv.get("amount_paid", 0))
            for inv in invoices
        ),
        2,
    )
