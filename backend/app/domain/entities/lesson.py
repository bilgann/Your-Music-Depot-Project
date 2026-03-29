from dataclasses import dataclass
from typing import Optional

from backend.app.domain.value_objects.financial.money import Money
from backend.app.domain.value_objects.financial.rate import Rate
from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
from backend.app.domain.value_objects.scheduling.time_slot import TimeSlot


@dataclass
class LessonEntity:
    """A scheduled lesson in a room with an instructor."""
    lesson_id: str
    instructor_id: str
    room_id: str
    time_slot: TimeSlot
    rate: Optional[Rate] = None
    status: Optional[str] = None
    recurrence: Optional[RecurrenceRule] = None

    @classmethod
    def from_dict(cls, d: dict) -> "LessonEntity":
        raw_rate = d.get("rate")
        raw_rec = d.get("recurrence")
        return cls(
            lesson_id=d["lesson_id"],
            instructor_id=d["instructor_id"],
            room_id=d["room_id"],
            time_slot=TimeSlot(
                start_time=d["start_time"],
                end_time=d["end_time"],
            ),
            rate=Rate.one_time(Money.of(raw_rate)) if raw_rate is not None else None,
            status=d.get("status"),
            recurrence=RecurrenceRule.from_str(raw_rec) if raw_rec else None,
        )

    def to_dict(self) -> dict:
        return {
            "lesson_id": self.lesson_id,
            "instructor_id": self.instructor_id,
            "room_id": self.room_id,
            "start_time": self.time_slot.start_time,
            "end_time": self.time_slot.end_time,
            "rate": self.rate.amount.amount if self.rate else None,
            "status": self.status,
            "recurrence": str(self.recurrence) if self.recurrence else None,
        }
