from dataclasses import dataclass, field
from typing import Optional

from backend.app.domain.value_objects.financial.money import Money
from backend.app.domain.value_objects.financial.rate import Rate
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime


@dataclass
class InstructorEntity:
    """A music instructor who delivers lessons.

    Identity and contact details live on the linked PersonEntity.
    blocked_times lists periods of unavailability (holidays, vacation, etc.).
    """
    instructor_id: str
    person_id: str
    hourly_rate: Optional[Rate] = None
    blocked_times: list[BlockedTime] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "InstructorEntity":
        raw_rate = d.get("hourly_rate")
        return cls(
            instructor_id=d["instructor_id"],
            person_id=d["person_id"],
            hourly_rate=(
                Rate.hourly(Money.of(raw_rate)) if raw_rate is not None else None
            ),
            blocked_times=[
                BlockedTime.from_dict(b) for b in d.get("blocked_times", [])
            ],
        )

    def to_dict(self) -> dict:
        return {
            "instructor_id": self.instructor_id,
            "person_id": self.person_id,
            "hourly_rate": self.hourly_rate.amount.amount if self.hourly_rate else None,
            "blocked_times": [b.to_dict() for b in self.blocked_times],
        }
