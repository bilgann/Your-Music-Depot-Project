from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """A non-negative monetary amount in a given currency."""
    amount: float
    currency: str = "CAD"

    def __add__(self, other: "Money") -> "Money":
        _assert_same_currency(self, other)
        return Money(round(self.amount + other.amount, 2), self.currency)

    def __sub__(self, other: "Money") -> "Money":
        _assert_same_currency(self, other)
        return Money(round(self.amount - other.amount, 2), self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"

    def to_dict(self) -> dict:
        return {"amount": self.amount, "currency": self.currency}

    @classmethod
    def zero(cls, currency: str = "CAD") -> "Money":
        return cls(0.0, currency)

    @classmethod
    def of(cls, amount: float, currency: str = "CAD") -> "Money":
        return cls(round(float(amount), 2), currency)


def _assert_same_currency(a: Money, b: Money) -> None:
    if a.currency != b.currency:
        raise ValueError(f"Currency mismatch: {a.currency} vs {b.currency}")
