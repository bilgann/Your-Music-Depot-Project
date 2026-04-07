from dataclasses import dataclass

from backend.app.domain.exceptions.exceptions import ValidationError


@dataclass(frozen=True)
class InvoiceStatus:
    """Valid states an invoice can be in."""
    value: str

    PENDING = "Pending"
    PARTIAL = "Partial"
    PAID = "Paid"
    CANCELLED = "Cancelled"

    VALID: frozenset = frozenset({"Pending", "Partial", "Paid", "Cancelled"})

    def __post_init__(self):
        if self.value not in self.VALID:
            raise ValidationError([{
                "field": "status",
                "message": f"Invalid invoice status '{self.value}'. Must be one of: {', '.join(sorted(self.VALID))}.",
            }])

    def __str__(self) -> str:
        return self.value

    def is_terminal(self) -> bool:
        return self.value in (self.PAID, self.CANCELLED)
