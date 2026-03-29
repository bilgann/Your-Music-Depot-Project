from dataclasses import dataclass


@dataclass(frozen=True)
class DateRange:
    """An inclusive calendar date range (ISO strings)."""
    period_start: str
    period_end: str

    @classmethod
    def from_dict(cls, d: dict) -> "DateRange":
        return cls(period_start=d["period_start"], period_end=d["period_end"])

    def to_dict(self) -> dict:
        return {"period_start": self.period_start, "period_end": self.period_end}
