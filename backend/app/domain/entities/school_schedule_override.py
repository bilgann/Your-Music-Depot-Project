from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SchoolScheduleOverrideEntity:
    """An exemption granting a specific entity immunity from a school schedule entry."""

    override_id: str
    schedule_id: str
    entity_type: str          # 'instructor' | 'room' | 'lesson' | 'course'
    entity_id: str
    reason: str = ""
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> SchoolScheduleOverrideEntity:
        return cls(
            override_id=d["override_id"],
            schedule_id=d["schedule_id"],
            entity_type=d["entity_type"],
            entity_id=d["entity_id"],
            reason=d.get("reason", ""),
            created_at=d.get("created_at"),
        )

    def to_dict(self) -> dict:
        return {
            "override_id": self.override_id,
            "schedule_id": self.schedule_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "reason": self.reason,
            "created_at": self.created_at,
        }
