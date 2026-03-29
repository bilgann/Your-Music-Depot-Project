from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering

from backend.app.domain.exceptions.exceptions import ValidationError

_RANKS: dict[str, int] = {
    "beginner":     1,
    "elementary":   2,
    "intermediate": 3,
    "advanced":     4,
    "professional": 5,
}


@total_ordering
@dataclass(frozen=True, eq=False)
class SkillLevel:
    """An ordered skill level used for students and instructor credentials.

    Levels (lowest → highest):
        beginner · elementary · intermediate · advanced · professional

    Supports full comparison:
        SkillLevel("beginner") < SkillLevel("advanced")   # True
        SkillLevel("advanced") >= SkillLevel("advanced")  # True
    """

    value: str

    def __post_init__(self):
        if self.value not in _RANKS:
            raise ValidationError([{
                "field": "skill_level",
                "message": (
                    f"Invalid skill level '{self.value}'. "
                    f"Must be one of: {', '.join(_RANKS)}."
                ),
            }])

    @property
    def rank(self) -> int:
        return _RANKS[self.value]

    # ── Comparison ────────────────────────────────────────────────────────────

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SkillLevel):
            return NotImplemented
        return self.rank == other.rank

    def __lt__(self, other: SkillLevel) -> bool:
        if not isinstance(other, SkillLevel):
            return NotImplemented
        return self.rank < other.rank

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {"value": self.value, "rank": self.rank}

    @classmethod
    def from_dict(cls, d: dict) -> "SkillLevel":
        return cls(d["value"])


# ── Class-level constants ─────────────────────────────────────────────────────

SkillLevel.BEGINNER     = SkillLevel("beginner")
SkillLevel.ELEMENTARY   = SkillLevel("elementary")
SkillLevel.INTERMEDIATE = SkillLevel("intermediate")
SkillLevel.ADVANCED     = SkillLevel("advanced")
SkillLevel.PROFESSIONAL = SkillLevel("professional")

SkillLevel.ALL: list[SkillLevel] = [
    SkillLevel.BEGINNER,
    SkillLevel.ELEMENTARY,
    SkillLevel.INTERMEDIATE,
    SkillLevel.ADVANCED,
    SkillLevel.PROFESSIONAL,
]
