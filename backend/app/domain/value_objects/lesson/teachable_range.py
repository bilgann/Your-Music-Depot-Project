from dataclasses import dataclass

from backend.app.domain.exceptions.exceptions import ValidationError
from backend.app.domain.value_objects.lesson.skill_level import SkillLevel


@dataclass(frozen=True)
class TeachableRange:
    """The range of skill levels an instructor is qualified to teach.

    Examples:
        TeachableRange(SkillLevel.BEGINNER, SkillLevel.INTERMEDIATE)
            # can teach beginner, elementary, and intermediate students

        TeachableRange(SkillLevel.ADVANCED, SkillLevel.PROFESSIONAL)
            # advanced / professional students only

        range.includes(SkillLevel.ELEMENTARY)  # True / False
    """

    min_level: SkillLevel
    max_level: SkillLevel

    def __post_init__(self):
        if self.min_level > self.max_level:
            raise ValidationError([{
                "field": "teachable_range",
                "message": (
                    f"min_level '{self.min_level}' must not exceed "
                    f"max_level '{self.max_level}'."
                ),
            }])

    def includes(self, level: SkillLevel) -> bool:
        """Return True if the given skill level falls within this range."""
        return self.min_level <= level <= self.max_level

    def __str__(self) -> str:
        return f"{self.min_level} – {self.max_level}"

    def to_dict(self) -> dict:
        return {
            "min_level": self.min_level.value,
            "max_level": self.max_level.value,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TeachableRange":
        return cls(
            min_level=SkillLevel(d["min_level"]),
            max_level=SkillLevel(d["max_level"]),
        )
