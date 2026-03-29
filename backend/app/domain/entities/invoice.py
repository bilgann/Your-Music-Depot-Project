from dataclasses import dataclass, field
from typing import Optional

from backend.app.domain.value_objects.financial.money import Money
from backend.app.domain.value_objects.scheduling.date_range import DateRange


@dataclass
class InvoiceEntity:
    """A billing invoice for a student covering a calendar period."""
    invoice_id: str
    student_id: str
    period: DateRange
    total_amount: Money
    amount_paid: Money = field(default_factory=Money.zero)
    status: str = "Pending"
    client_id: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "InvoiceEntity":
        return cls(
            invoice_id=d["invoice_id"],
            student_id=d["student_id"],
            period=DateRange(
                period_start=d["period_start"],
                period_end=d["period_end"],
            ),
            total_amount=Money.of(d["total_amount"]),
            amount_paid=Money.of(d.get("amount_paid") or 0),
            status=d.get("status", "Pending"),
            client_id=d.get("client_id"),
        )

    @property
    def outstanding(self) -> Money:
        return self.total_amount - self.amount_paid

    def to_dict(self) -> dict:
        return {
            "invoice_id": self.invoice_id,
            "student_id": self.student_id,
            "client_id": self.client_id,
            "period_start": self.period.period_start,
            "period_end": self.period.period_end,
            "total_amount": self.total_amount.amount,
            "amount_paid": self.amount_paid.amount,
            "status": self.status,
        }
