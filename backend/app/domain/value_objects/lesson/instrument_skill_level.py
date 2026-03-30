from dataclasses import dataclass

from backend.app.domain.value_objects.lesson.instrument import Instrument
from backend.app.domain.value_objects.lesson.skill_level import SkillLevel


@dataclass(frozen=True)
class InstrumentSkillLevel:
    """A student's skill level for a specific instrument.

    Unlike InstrumentProficiency (which uses a TeachableRange for instructors),
    this represents a single point-in-time skill level for a student on one
    instrument.

    Examples:
        InstrumentSkillLevel(Instrument("Piano", "keyboard"), SkillLevel("intermediate"))
        InstrumentSkillLevel(Instrument("Voice", "voice"),    SkillLevel("beginner"))
    """

    instrument: Instrument
    skill_level: SkillLevel

    def to_dict(self) -> dict:
        return {
            "name": self.instrument.name,
            "family": self.instrument.family,
            "skill_level": self.skill_level.value,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "InstrumentSkillLevel":
        return cls(
            instrument=Instrument(name=d["name"], family=d["family"]),
            skill_level=SkillLevel(d["skill_level"]),
        )
