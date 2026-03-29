"""
TeachingRequirement value object.

A single condition that must be satisfied for a student-instructor pairing to
be valid.  The same VO is used in two directions:

  StudentEntity.requirements   — what the student needs the instructor to have
  InstructorEntity.restrictions — conditions on students the instructor accepts

requirement_type values
-----------------------
"credential"      (student side)  — instructor must hold an active credential of
                                    this type  (e.g. "cpr", "special_ed")
"min_student_age" (instructor side) — student must be at least this age (int str)
"max_student_age" (instructor side) — student must be at most this age (int str)
"""

from __future__ import annotations

from dataclasses import dataclass

VALID_TYPES = frozenset({"credential", "min_student_age", "max_student_age"})


@dataclass(frozen=True)
class TeachingRequirement:
    requirement_type: str   # one of VALID_TYPES
    value: str              # credential type string, or age as digit string

    def __post_init__(self) -> None:
        if self.requirement_type not in VALID_TYPES:
            raise ValueError(
                f"requirement_type must be one of {sorted(VALID_TYPES)}, "
                f"got {self.requirement_type!r}"
            )
        if not self.value:
            raise ValueError("TeachingRequirement value must not be empty.")
        if self.requirement_type in {"min_student_age", "max_student_age"}:
            if not self.value.isdigit():
                raise ValueError(
                    f"{self.requirement_type} value must be a non-negative integer "
                    f"string, got {self.value!r}"
                )

    # ── Factories ─────────────────────────────────────────────────────────────

    @classmethod
    def credential(cls, credential_type: str) -> "TeachingRequirement":
        """Student requires the instructor to hold an active credential of this type."""
        return cls(requirement_type="credential", value=credential_type)

    @classmethod
    def min_student_age(cls, age: int) -> "TeachingRequirement":
        """Instructor will not teach students younger than `age`."""
        return cls(requirement_type="min_student_age", value=str(age))

    @classmethod
    def max_student_age(cls, age: int) -> "TeachingRequirement":
        """Instructor will not teach students older than `age`."""
        return cls(requirement_type="max_student_age", value=str(age))

    # ── Serialisation ─────────────────────────────────────────────────────────

    @classmethod
    def from_dict(cls, d: dict) -> "TeachingRequirement":
        return cls(
            requirement_type=d["requirement_type"],
            value=d["value"],
        )

    def to_dict(self) -> dict:
        return {
            "requirement_type": self.requirement_type,
            "value": self.value,
        }
