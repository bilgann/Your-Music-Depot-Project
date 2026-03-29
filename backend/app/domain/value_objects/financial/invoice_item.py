"""
InvoiceItem value object.

A single line item on an invoice.  Most items are lesson charges, but an
invoice may also include non-lesson charges such as instrument damage fees
or instrument purchases.

item_type values
----------------
"lesson"               Regular lesson charge (present, late-cancel, etc.)
"instrument_damage"    Charge for damage to a school-owned instrument.
"instrument_purchase"  Sale of an instrument to the student / client.
"other"                Anything else (admin fee, late-payment penalty, etc.)

lesson_id is only set for "lesson" items; it is None for all other types.
amount may be negative for discounts, credits, or adjustments.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from backend.app.domain.value_objects.financial.money import Money

VALID_ITEM_TYPES = frozenset({
    "lesson",
    "instrument_damage",
    "instrument_purchase",
    "other",
})


@dataclass(frozen=True)
class InvoiceItem:
    item_type:         str            # one of VALID_ITEM_TYPES
    description:       str
    amount:            Money
    lesson_id:         Optional[str] = None   # set only for item_type="lesson"
    attendance_status: Optional[str] = None   # set only for item_type="lesson"

    def __post_init__(self) -> None:
        if self.item_type not in VALID_ITEM_TYPES:
            raise ValueError(
                f"item_type must be one of {sorted(VALID_ITEM_TYPES)}, "
                f"got {self.item_type!r}"
            )
        if self.item_type != "lesson" and self.lesson_id is not None:
            raise ValueError(
                "lesson_id must be None for non-lesson invoice items."
            )

    # ── Factories ─────────────────────────────────────────────────────────────

    @classmethod
    def for_lesson(
        cls,
        lesson_id: str,
        description: str,
        amount: Money,
        attendance_status: Optional[str] = None,
    ) -> "InvoiceItem":
        return cls(
            item_type="lesson",
            description=description,
            amount=amount,
            lesson_id=lesson_id,
            attendance_status=attendance_status,
        )

    @classmethod
    def for_instrument_damage(cls, description: str, amount: Money) -> "InvoiceItem":
        return cls(item_type="instrument_damage", description=description, amount=amount)

    @classmethod
    def for_instrument_purchase(cls, description: str, amount: Money) -> "InvoiceItem":
        return cls(item_type="instrument_purchase", description=description, amount=amount)

    @classmethod
    def other(cls, description: str, amount: Money) -> "InvoiceItem":
        return cls(item_type="other", description=description, amount=amount)

    # ── Serialisation ─────────────────────────────────────────────────────────

    @classmethod
    def from_dict(cls, d: dict) -> "InvoiceItem":
        return cls(
            item_type=d.get("item_type", "lesson"),
            description=d["description"],
            amount=Money.of(d["amount"]),
            lesson_id=d.get("lesson_id"),
            attendance_status=d.get("attendance_status"),
        )

    def to_dict(self) -> dict:
        return {
            "item_type":         self.item_type,
            "description":       self.description,
            "amount":            self.amount.amount,
            "lesson_id":         self.lesson_id,
            "attendance_status": self.attendance_status,
        }
