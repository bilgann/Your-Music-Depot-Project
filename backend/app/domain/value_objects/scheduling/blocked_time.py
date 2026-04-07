from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from backend.app.domain.exceptions.exceptions import ValidationError
from backend.app.domain.value_objects.scheduling.date_range import DateRange
from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule

_BLOCK_TYPES: frozenset[str] = frozenset({
    "holiday",
    "weekend",
    "work",
    "school",
    "vacation",
    "personal",
    "other",
})


@dataclass(frozen=True)
class BlockedTime:
    """A period of unavailability in the schedule.

    Exactly one of `date`, `date_range`, or `recurrence` must be set:
      date        — a single blocked day (e.g. a public holiday)
      date_range  — a contiguous block of days (e.g. a vacation)
      recurrence  — a repeating pattern (e.g. every weekend, every Monday)

    Examples:
        BlockedTime.holiday("Christmas Day", "2025-12-25")
        BlockedTime.holiday("New Year's", "2026-01-01")

        BlockedTime.vacation("Summer Break",
            DateRange("2025-07-14", "2025-07-28"))

        BlockedTime.recurring("Weekends",
            RecurrenceRule.cron("0 0 * * SAT,SUN"), block_type="weekend")

        BlockedTime.recurring("Mondays Off",
            RecurrenceRule.cron("0 0 * * MON"), block_type="personal")
    """

    label: str
    block_type: str
    date: Optional[str] = None
    date_range: Optional[DateRange] = None
    recurrence: Optional[RecurrenceRule] = None

    def __post_init__(self):
        if not self.label or not self.label.strip():
            raise ValidationError([{
                "field": "label",
                "message": "BlockedTime label must not be blank.",
            }])

        if self.block_type not in _BLOCK_TYPES:
            raise ValidationError([{
                "field": "block_type",
                "message": (
                    f"Invalid block type '{self.block_type}'. "
                    f"Must be one of: {', '.join(sorted(_BLOCK_TYPES))}."
                ),
            }])

        set_fields = sum([
            self.date is not None,
            self.date_range is not None,
            self.recurrence is not None,
        ])
        if set_fields != 1:
            raise ValidationError([{
                "field": "blocked_time",
                "message": "Exactly one of 'date', 'date_range', or 'recurrence' must be set.",
            }])

    # ── Convenience constructors ──────────────────────────────────────────────

    @classmethod
    def holiday(cls, label: str, date: str) -> "BlockedTime":
        """A single-day public or observed holiday."""
        return cls(label=label, block_type="holiday", date=date)

    @classmethod
    def vacation(cls, label: str, date_range: DateRange) -> "BlockedTime":
        """A contiguous block of days off."""
        return cls(label=label, block_type="vacation", date_range=date_range)

    @classmethod
    def recurring(
        cls,
        label: str,
        recurrence: RecurrenceRule,
        block_type: str = "other",
    ) -> "BlockedTime":
        """A repeating unavailability pattern (cron-based)."""
        return cls(label=label, block_type=block_type, recurrence=recurrence)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def is_recurring(self) -> bool:
        return self.recurrence is not None

    @property
    def is_single_day(self) -> bool:
        return self.date is not None

    @property
    def is_range(self) -> bool:
        return self.date_range is not None

    def includes_date(self, iso_date: str) -> bool:
        """Return True if the given ISO date falls within this blocked period.

        Note: recurrence patterns require external evaluation (e.g. a cron
        library) — this method returns False for recurring blocks so callers
        can handle them separately.
        """
        if self.date is not None:
            return self.date == iso_date
        if self.date_range is not None:
            return self.date_range.period_start <= iso_date <= self.date_range.period_end
        return False  # recurring — needs cron evaluation

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "block_type": self.block_type,
            "date": self.date,
            "date_range": self.date_range.to_dict() if self.date_range else None,
            "recurrence": self.recurrence.to_dict() if self.recurrence else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BlockedTime":
        raw_range = d.get("date_range")
        raw_rec = d.get("recurrence")
        return cls(
            label=d["label"],
            block_type=d["block_type"],
            date=d.get("date"),
            date_range=DateRange.from_dict(raw_range) if raw_range else None,
            recurrence=RecurrenceRule.from_dict(raw_rec) if raw_rec else None,
        )
