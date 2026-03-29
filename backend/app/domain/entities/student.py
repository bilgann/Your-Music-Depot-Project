from dataclasses import dataclass
from typing import Optional

from backend.app.domain.value_objects.lesson.skill_level import SkillLevel


@dataclass
class StudentEntity:
    """A student who enrolls in lessons and is billed via invoices."""
    student_id: str
    person_id: str
    client_id: Optional[str] = None
    skill_level: Optional[SkillLevel] = None

    @classmethod
    def from_dict(cls, d: dict) -> "StudentEntity":
        raw_level = d.get("skill_level")
        return cls(
            student_id=d["student_id"],
            person_id=d["person_id"],
            client_id=d.get("client_id"),
            skill_level=SkillLevel(raw_level) if raw_level else None,
        )

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "person_id": self.person_id,
            "client_id": self.client_id,
            "skill_level": self.skill_level.value if self.skill_level else None,
        }
