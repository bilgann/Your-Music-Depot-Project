from dataclasses import dataclass, field
from typing import Optional

from backend.app.domain.value_objects.compatibility.teaching_requirement import TeachingRequirement
from backend.app.domain.value_objects.lesson.skill_level import SkillLevel


@dataclass
class StudentEntity:
    """A student who enrolls in lessons and is billed via invoices.

    age          Used by CompatibilityService to enforce instructor age restrictions.
    requirements List of TeachingRequirements the student's assigned instructor must
                 satisfy (e.g. active CPR credential, special-ed certification).
    """
    student_id:   str
    person_id:    str
    client_id:    Optional[str] = None
    skill_level:  Optional[SkillLevel] = None
    age:          Optional[int] = None
    requirements: list[TeachingRequirement] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "StudentEntity":
        raw_level = d.get("skill_level")
        return cls(
            student_id=d["student_id"],
            person_id=d["person_id"],
            client_id=d.get("client_id"),
            skill_level=SkillLevel(raw_level) if raw_level else None,
            age=d.get("age"),
            requirements=[
                TeachingRequirement.from_dict(r) for r in d.get("requirements", [])
            ],
        )

    def to_dict(self) -> dict:
        return {
            "student_id":   self.student_id,
            "person_id":    self.person_id,
            "client_id":    self.client_id,
            "skill_level":  self.skill_level.value if self.skill_level else None,
            "age":          self.age,
            "requirements": [r.to_dict() for r in self.requirements],
        }
