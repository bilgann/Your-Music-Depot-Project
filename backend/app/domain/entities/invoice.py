from dataclasses import dataclass, field
from typing import Optional

from backend.app.domain.value_objects.financial.invoice_item import InvoiceItem
from backend.app.domain.value_objects.financial.money import Money
from backend.app.domain.value_objects.scheduling.date_range import DateRange


@dataclass
class InvoiceEntity:
    """A billing invoice for a student covering a calendar period.

    items         All line items on this invoice — lesson charges, instrument
                  damage fees, instrument purchases, and any other charges or
                  credits.  total_amount is derived by summing them.
    amount_paid   Running total of payments applied to this invoice.
    outstanding   Computed: total_amount − amount_paid.
    """
    invoice_id:  str
    student_id:  str
    period:      DateRange
    items:       list[InvoiceItem] = field(default_factory=list)
    amount_paid: Money = field(default_factory=Money.zero)
    status:      str = "Pending"
    client_id:   Optional[str] = None

    # ── Computed properties ───────────────────────────────────────────────────

    @property
    def total_amount(self) -> Money:
        """Sum of all item amounts (may include negative adjustment lines)."""
        total = Money.zero()
        for item in self.items:
            total = total + item.amount
        return total

    @property
    def outstanding(self) -> Money:
        return self.total_amount - self.amount_paid

    # ── Convenience helpers ───────────────────────────────────────────────────

    def lesson_items(self) -> list[InvoiceItem]:
        return [i for i in self.items if i.item_type == "lesson"]

    def non_lesson_items(self) -> list[InvoiceItem]:
        return [i for i in self.items if i.item_type != "lesson"]

    # ── Serialisation ─────────────────────────────────────────────────────────

    @classmethod
    def from_dict(cls, d: dict) -> "InvoiceEntity":
        return cls(
            invoice_id=d["invoice_id"],
            student_id=d["student_id"],
            period=DateRange(
                period_start=d["period_start"],
                period_end=d["period_end"],
            ),
            items=[InvoiceItem.from_dict(i) for i in d.get("items", [])],
            amount_paid=Money.of(d.get("amount_paid") or 0),
            status=d.get("status", "Pending"),
            client_id=d.get("client_id"),
        )

    def to_dict(self) -> dict:
        return {
            "invoice_id":   self.invoice_id,
            "student_id":   self.student_id,
            "client_id":    self.client_id,
            "period_start": self.period.period_start,
            "period_end":   self.period.period_end,
            "items":        [i.to_dict() for i in self.items],
            "total_amount": self.total_amount.amount,   # denormalised for reads
            "amount_paid":  self.amount_paid.amount,
            "status":       self.status,
        }
