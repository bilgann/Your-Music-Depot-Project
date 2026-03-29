"""
InstructorStudentCompatibilityEntity

Records an explicit preference or restriction between a specific instructor and
a specific student.  The CompatibilityService uses these as hard constraints
(BLOCKED / REQUIRED) or soft booking signals (DISLIKED / PREFERRED).

Fields
------
compatibility_id  Surrogate key.
instructor_id     The instructor this record applies to.
student_id        The student this record applies to.
verdict           One of the CompatibilityVerdict constants.
reason            Human-readable explanation stored for audit purposes.
                  Examples: "student request", "instructor request", "safeguarding"
initiated_by      Who recorded this override: "student" | "instructor" | "admin".
"""

from dataclasses import dataclass

from backend.app.domain.value_objects.compatibility.compatibility_verdict import (
    ALL_VERDICTS,
)

VALID_INITIATORS = frozenset({"student", "instructor", "admin"})


@dataclass
class InstructorStudentCompatibilityEntity:
    compatibility_id: str
    instructor_id:    str
    student_id:       str
    verdict:          str   # CompatibilityVerdict constant
    reason:           str
    initiated_by:     str   # "student" | "instructor" | "admin"

    def __post_init__(self) -> None:
        if self.verdict not in ALL_VERDICTS:
            raise ValueError(
                f"verdict must be one of {sorted(ALL_VERDICTS)}, got {self.verdict!r}"
            )
        if self.initiated_by not in VALID_INITIATORS:
            raise ValueError(
                f"initiated_by must be one of {sorted(VALID_INITIATORS)}, "
                f"got {self.initiated_by!r}"
            )

    @classmethod
    def from_dict(cls, d: dict) -> "InstructorStudentCompatibilityEntity":
        return cls(
            compatibility_id=d["compatibility_id"],
            instructor_id=d["instructor_id"],
            student_id=d["student_id"],
            verdict=d["verdict"],
            reason=d.get("reason", ""),
            initiated_by=d["initiated_by"],
        )

    def to_dict(self) -> dict:
        return {
            "compatibility_id": self.compatibility_id,
            "instructor_id":    self.instructor_id,
            "student_id":       self.student_id,
            "verdict":          self.verdict,
            "reason":           self.reason,
            "initiated_by":     self.initiated_by,
        }
