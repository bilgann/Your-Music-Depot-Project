from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
from backend.app.domain.value_objects.scheduling.date_range import DateRange
from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule


@dataclass
class SchoolScheduleEntity:
    """A school-wide blocked time entry (holiday, vacation, closure)."""

    schedule_id: str
    label: str
    block_type: str
    date: Optional[str] = None
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    recurrence: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None

    def to_blocked_time(self) -> BlockedTime:
        """Convert to a BlockedTime for use in schedule projection."""
        if self.date:
            return BlockedTime(
                label=self.label, block_type=self.block_type, date=self.date,
            )
        if self.date_range_start and self.date_range_end:
            return BlockedTime(
                label=self.label,
                block_type=self.block_type,
                date_range=DateRange(
                    period_start=self.date_range_start,
                    period_end=self.date_range_end,
                ),
            )
        if self.recurrence:
            return BlockedTime(
                label=self.label,
                block_type=self.block_type,
                recurrence=RecurrenceRule.cron(self.recurrence),
            )
        raise ValueError("SchoolScheduleEntity has no date, date_range, or recurrence.")

    @classmethod
    def from_dict(cls, d: dict) -> SchoolScheduleEntity:
        return cls(
            schedule_id=d["schedule_id"],
            label=d["label"],
            block_type=d["block_type"],
            date=str(d["date"]) if d.get("date") else None,
            date_range_start=str(d["date_range_start"]) if d.get("date_range_start") else None,
            date_range_end=str(d["date_range_end"]) if d.get("date_range_end") else None,
            recurrence=d.get("recurrence"),
            is_active=d.get("is_active", True),
            created_at=d.get("created_at"),
        )

    def to_dict(self) -> dict:
        return {
            "schedule_id": self.schedule_id,
            "label": self.label,
            "block_type": self.block_type,
            "date": self.date,
            "date_range_start": self.date_range_start,
            "date_range_end": self.date_range_end,
            "recurrence": self.recurrence,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }
