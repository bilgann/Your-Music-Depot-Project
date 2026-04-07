from dataclasses import dataclass

from backend.app.domain.exceptions.exceptions import ValidationError


_VALID_RECURRENCE_TYPES: frozenset = frozenset({"one_time", "cron"})


@dataclass(frozen=True)
class RecurrenceRule:
    """Describes when a lesson occurs — either a one-time date or a cron schedule.

    rule_type: "one_time" | "cron"
    value:
        one_time → ISO date string, e.g. "2025-09-01"
        cron     → cron expression, e.g. "0 15 * * MON"  (every Monday at 15:00)

    Examples:
        RecurrenceRule.one_time("2025-09-01")       # single lesson on Sep 1
        RecurrenceRule.cron("0 15 * * MON")         # every Monday at 15:00
        RecurrenceRule.cron("0 10 * * MON,WED,FRI") # Mon/Wed/Fri at 10:00
        RecurrenceRule.cron("0 14 1 * *")           # 1st of every month at 14:00
    """

    rule_type: str
    value: str

    def __post_init__(self):
        if self.rule_type not in _VALID_RECURRENCE_TYPES:
            raise ValidationError([{
                "field": "recurrence",
                "message": (
                    f"Invalid recurrence type '{self.rule_type}'. "
                    f"Must be one of: {', '.join(sorted(_VALID_RECURRENCE_TYPES))}."
                ),
            }])
        if not self.value or not self.value.strip():
            raise ValidationError([{
                "field": "recurrence",
                "message": "Recurrence value must not be blank.",
            }])

    # ── Convenience constructors ──────────────────────────────────────────────

    @classmethod
    def one_time(cls, date: str) -> "RecurrenceRule":
        """Single occurrence on the given ISO date (YYYY-MM-DD)."""
        return cls(rule_type="one_time", value=date)

    @classmethod
    def cron(cls, expression: str) -> "RecurrenceRule":
        """Repeating schedule expressed as a cron expression."""
        return cls(rule_type="cron", value=expression)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def is_recurring(self) -> bool:
        return self.rule_type == "cron"

    def __str__(self) -> str:
        return self.value

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {"rule_type": self.rule_type, "value": self.value}

    @classmethod
    def from_dict(cls, d: dict) -> "RecurrenceRule":
        return cls(rule_type=d["rule_type"], value=d["value"])

    @classmethod
    def from_str(cls, raw: str) -> "RecurrenceRule":
        """
        Parse a raw recurrence string stored in the DB.
        Strings with 5 space-separated fields are treated as cron expressions;
        anything else is treated as a one-time ISO date.
        """
        raw = raw.strip()
        if len(raw.split()) == 5:
            return cls.cron(raw)
        return cls.one_time(raw)
