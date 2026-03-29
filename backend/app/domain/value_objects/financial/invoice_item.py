from dataclasses import dataclass

from backend.app.domain.value_objects.financial.money import Money


@dataclass(frozen=True)
class InvoiceItem:
    """A single line item on an invoice, representing one lesson charge.

    Examples:
        InvoiceItem(                              # present — full rate
            lesson_id="abc",
            description="Present — 2025-03-01",
            amount=Money.of(40.00),
            attendance_status="present",
        )
        InvoiceItem(                              # late cancel — policy applied
            lesson_id="def",
            description="Late cancellation — 2025-03-08",
            amount=Money.of(20.00),
            attendance_status="late_cancel",
        )
        InvoiceItem(                              # discount / makeup credit
            lesson_id="ghi",
            description="Sibling discount — 2025-03-15",
            amount=Money.of(-5.00),
            attendance_status="present",
        )
    """
    lesson_id: str
    description: str
    amount: Money
    attendance_status: str | None = None

    def to_dict(self) -> dict:
        return {
            "lesson_id": self.lesson_id,
            "description": self.description,
            "amount": self.amount.amount,
            "attendance_status": self.attendance_status,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "InvoiceItem":
        return cls(
            lesson_id=d["lesson_id"],
            description=d["description"],
            amount=Money.of(d["amount"]),
            attendance_status=d.get("attendance_status"),
        )
