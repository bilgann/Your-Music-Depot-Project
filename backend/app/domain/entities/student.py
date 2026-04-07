from dataclasses import dataclass, field
from typing import Optional

from backend.app.domain.value_objects.compatibility.teaching_requirement import TeachingRequirement
from backend.app.domain.value_objects.lesson.instrument_skill_level import InstrumentSkillLevel


@dataclass
class StudentEntity:
    """A student who enrolls in lessons and is billed via invoices.

    age                     Used by CompatibilityService to enforce instructor
                            age restrictions.
    instrument_skill_levels Per-instrument skill levels (e.g. Piano/intermediate,
                            Voice/beginner).  Replaces the old single skill_level.
    requirements            List of TeachingRequirements the student's assigned
                            instructor must satisfy (e.g. active CPR credential).
    """
    student_id:              str
    person_id:               str
    client_id:               Optional[str] = None
    age:                     Optional[int] = None
    instrument_skill_levels: list[InstrumentSkillLevel] = field(default_factory=list)
    requirements:            list[TeachingRequirement] = field(default_factory=list)

    def skill_level_for(self, instrument_name: str, instrument_family: str):
        """Return the SkillLevel for a specific instrument, or None."""
        for isl in self.instrument_skill_levels:
            if (isl.instrument.name == instrument_name
                    and isl.instrument.family == instrument_family):
                return isl.skill_level
        return None

    @classmethod
    def from_dict(cls, d: dict) -> "StudentEntity":
        return cls(
            student_id=d["student_id"],
            person_id=d["person_id"],
            client_id=d.get("client_id"),
            age=d.get("age"),
            instrument_skill_levels=[
                InstrumentSkillLevel.from_dict(r)
                for r in d.get("instrument_skill_levels", [])
            ],
            requirements=[
                TeachingRequirement.from_dict(r) for r in d.get("requirements", [])
            ],
        )

    def to_dict(self) -> dict:
        return {
            "student_id":              self.student_id,
            "person_id":               self.person_id,
            "client_id":               self.client_id,
            "age":                     self.age,
            "instrument_skill_levels": [i.to_dict() for i in self.instrument_skill_levels],
            "requirements":            [r.to_dict() for r in self.requirements],
        }
