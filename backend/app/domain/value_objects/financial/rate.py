from dataclasses import dataclass

from backend.app.domain.exceptions.exceptions import ValidationError
from backend.app.domain.value_objects.financial.money import Money


@dataclass(frozen=True)
class Rate:
    """A monetary rate that is either one-time (flat) or hourly.

    charge_type: "one_time" | "hourly"
    amount:      the Money value of the rate

    Examples:
        Rate("one_time", Money.of(40))      # CAD 40 flat per lesson
        Rate("hourly",   Money.of(60))      # CAD 60 per hour
        Rate.one_time(Money.of(40))         # convenience constructor
        Rate.hourly(Money.of(60))           # convenience constructor

        # Compute the charge for a 45-minute lesson at an hourly rate:
        rate = Rate.hourly(Money.of(60))
        charge = rate.for_duration(minutes=45)   # → Money(45.00)
    """

    VALID_TYPES: frozenset = frozenset({"one_time", "hourly"})

    charge_type: str
    amount: Money

    def __post_init__(self):
        if self.charge_type not in self.VALID_TYPES:
            raise ValidationError([{
                "field": "charge_type",
                "message": f"Invalid rate type '{self.charge_type}'. Must be one of: {', '.join(sorted(self.VALID_TYPES))}.",
            }])

    # ── Convenience constructors ──────────────────────────────────────────────

    @classmethod
    def one_time(cls, amount: Money) -> "Rate":
        return cls(charge_type="one_time", amount=amount)

    @classmethod
    def hourly(cls, amount: Money) -> "Rate":
        return cls(charge_type="hourly", amount=amount)

    # ── Calculation ───────────────────────────────────────────────────────────

    def for_duration(self, minutes: float) -> Money:
        """Return the charge for a given duration.

        One-time rates ignore duration and return the full amount.
        Hourly rates are prorated by the fraction of an hour.
        """
        if self.charge_type == "hourly":
            return Money.of(self.amount.amount * minutes / 60, self.amount.currency)
        return self.amount

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "charge_type": self.charge_type,
            "amount": self.amount.amount,
            "currency": self.amount.currency,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Rate":
        return cls(
            charge_type=d["charge_type"],
            amount=Money.of(d["amount"], d.get("currency", "CAD")),
        )
