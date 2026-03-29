from dataclasses import dataclass

from backend.app.domain.value_objects.lesson.instrument import Instrument
from backend.app.domain.value_objects.lesson.teachable_range import TeachableRange


@dataclass(frozen=True)
class InstrumentProficiency:
    """An instrument paired with the skill-level range an instructor can teach.

    Used in credentials to express per-instrument expertise, allowing an
    instructor to be, for example, a beginner vocal teacher but an expert
    guitarist under the same credential.

    Examples:
        InstrumentProficiency(
            Instrument("Voice",  "voice"),
            TeachableRange(SkillLevel.BEGINNER, SkillLevel.INTERMEDIATE),
        )
        InstrumentProficiency(
            Instrument("Guitar", "strings"),
            TeachableRange(SkillLevel.BEGINNER, SkillLevel.PROFESSIONAL),
        )
    """

    instrument: Instrument
    teachable_range: TeachableRange

    def can_teach(self, instrument: Instrument, level) -> bool:
        """True if this proficiency covers the given instrument and skill level."""
        return self.instrument == instrument and self.teachable_range.includes(level)

    def to_dict(self) -> dict:
        return {
            "name": self.instrument.name,
            "family": self.instrument.family,
            "min_level": self.teachable_range.min_level.value,
            "max_level": self.teachable_range.max_level.value,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "InstrumentProficiency":
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        return cls(
            instrument=Instrument(name=d["name"], family=d["family"]),
            teachable_range=TeachableRange(
                min_level=SkillLevel(d["min_level"]),
                max_level=SkillLevel(d["max_level"]),
            ),
        )
