"""
Compatibility domain service.

Determines whether a specific instructor can be assigned to a specific student
by evaluating three independent layers of rules:

  1. Pair overrides (InstructorStudentCompatibilityEntity)
       Hard: BLOCKED → can_assign=False immediately.
             REQUIRED → recorded; soft signals are still collected.
       Soft: PREFERRED / DISLIKED → recorded as soft_verdict for booking hints.

  2. Instructor restrictions (TeachingRequirement on InstructorEntity)
       e.g. min_student_age=5 → student.age must be ≥ 5.

  3. Student requirements (TeachingRequirement on StudentEntity)
       e.g. credential("cpr") → instructor must hold an active CPR credential.

No database access.  The caller (application service) is responsible for
loading all relevant entities and passing them in.
"""

from __future__ import annotations

from backend.app.domain.entities.credential import CredentialEntity
from backend.app.domain.entities.instructor import InstructorEntity
from backend.app.domain.entities.instructor_student_compatibility import (
    InstructorStudentCompatibilityEntity,
)
from backend.app.domain.entities.student import StudentEntity
from backend.app.domain.value_objects.compatibility.compatibility_result import (
    CompatibilityResult,
)
from backend.app.domain.value_objects.compatibility.compatibility_verdict import (
    BLOCKED,
    DISLIKED,
    PREFERRED,
    REQUIRED,
)


def check(
    student:       StudentEntity,
    instructor:    InstructorEntity,
    credentials:   list[CredentialEntity],
    pair_overrides: list[InstructorStudentCompatibilityEntity],
) -> CompatibilityResult:
    """
    Evaluate whether `instructor` can be assigned to `student`.

    Args:
        student:        The student being assigned.
        instructor:     The candidate instructor.
        credentials:    All credentials belonging to the instructor
                        (expired ones are filtered internally).
        pair_overrides: All InstructorStudentCompatibilityEntity records for
                        this student-instructor pair (may include overrides for
                        other pairs — irrelevant ones are filtered internally).

    Returns:
        CompatibilityResult — check .can_assign before using the pairing.
    """
    reasons:      list[str] = []
    hard_verdict: str | None = None
    soft_verdict: str | None = None

    # ── 1. Pair overrides ─────────────────────────────────────────────────────
    for override in pair_overrides:
        if (override.instructor_id != instructor.instructor_id
                or override.student_id != student.student_id):
            continue

        if override.verdict == BLOCKED:
            return CompatibilityResult.blocked(
                f"{override.reason} (initiated by: {override.initiated_by})"
            )

        if override.verdict == REQUIRED:
            hard_verdict = REQUIRED
            reasons.append(
                f"Required pairing: {override.reason} "
                f"(initiated by: {override.initiated_by})"
            )

        elif override.verdict == PREFERRED:
            soft_verdict = PREFERRED
            reasons.append(
                f"Preferred pairing: {override.reason} "
                f"(initiated by: {override.initiated_by})"
            )

        elif override.verdict == DISLIKED:
            soft_verdict = DISLIKED
            reasons.append(
                f"Disliked pairing: {override.reason} "
                f"(initiated by: {override.initiated_by})"
            )

    # ── 2. Instructor restrictions vs student age ─────────────────────────────
    if student.age is not None:
        for restriction in instructor.restrictions:
            if restriction.requirement_type == "min_student_age":
                min_age = int(restriction.value)
                if student.age < min_age:
                    return CompatibilityResult.requirement_not_met(
                        f"Instructor requires students to be at least {min_age} years old "
                        f"(student is {student.age})."
                    )
            elif restriction.requirement_type == "max_student_age":
                max_age = int(restriction.value)
                if student.age > max_age:
                    return CompatibilityResult.requirement_not_met(
                        f"Instructor only teaches students up to {max_age} years old "
                        f"(student is {student.age})."
                    )

    # ── 3. Student requirements vs instructor credentials ─────────────────────
    active_credential_types = {
        c.credential_type
        for c in credentials
        if c.instructor_id == instructor.instructor_id and not c.is_expired
    }
    for requirement in student.requirements:
        if requirement.requirement_type == "credential":
            if requirement.value not in active_credential_types:
                return CompatibilityResult.requirement_not_met(
                    f"Instructor does not hold an active '{requirement.value}' credential "
                    f"required by this student."
                )

    return CompatibilityResult.ok(
        hard_verdict=hard_verdict,
        soft_verdict=soft_verdict,
        reasons=tuple(reasons),
    )


def filter_compatible(
    student:        StudentEntity,
    instructors:    list[InstructorEntity],
    credentials:    list[CredentialEntity],
    pair_overrides: list[InstructorStudentCompatibilityEntity],
) -> list[tuple[InstructorEntity, CompatibilityResult]]:
    """
    Filter a list of candidate instructors down to compatible ones.

    Returns a list of (instructor, result) pairs sorted so that:
      - REQUIRED pairings come first
      - PREFERRED pairings come before neutral
      - DISLIKED pairings come last (but are still included — caller decides)
      - Incompatible instructors (can_assign=False) are excluded entirely
    """
    compatible = [
        (instr, result)
        for instr in instructors
        if (result := check(student, instr, credentials, pair_overrides)).can_assign
    ]

    def _sort_key(pair: tuple[InstructorEntity, CompatibilityResult]) -> int:
        verdict = pair[1].hard_verdict or pair[1].soft_verdict
        return {REQUIRED: 0, PREFERRED: 1, None: 2, DISLIKED: 3}.get(verdict, 2)

    return sorted(compatible, key=_sort_key)
