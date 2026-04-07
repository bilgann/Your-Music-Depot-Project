"""
Unit tests for the compatibility domain service.

domain/services/compatibility_service.py

Tests cover:
  check()              — pair overrides (BLOCKED/REQUIRED/PREFERRED/DISLIKED),
                         instructor age restrictions, student credential requirements
  filter_compatible()  — filters and sort order
"""
import unittest

from backend.app.domain.entities.credential import CredentialEntity
from backend.app.domain.entities.instructor import InstructorEntity
from backend.app.domain.entities.instructor_student_compatibility import (
    InstructorStudentCompatibilityEntity,
)
from backend.app.domain.entities.student import StudentEntity
from backend.app.domain.value_objects.compatibility.teaching_requirement import TeachingRequirement
from backend.app.domain.value_objects.scheduling.date_range import DateRange


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _student(student_id="s1", age=None, requirements=None):
    return StudentEntity(
        student_id=student_id,
        person_id="p1",
        age=age,
        requirements=requirements or [],
    )


def _instructor(instructor_id="i1", restrictions=None):
    return InstructorEntity(
        instructor_id=instructor_id,
        person_id="p2",
        restrictions=restrictions or [],
    )


def _credential(instructor_id="i1", credential_type="cpr", expired=False):
    """Create a credential, optionally already expired."""
    return CredentialEntity(
        credential_id="cred-1",
        instructor_id=instructor_id,
        proficiencies=[],
        credential_type=credential_type,
        # If expired, end date is before today (2026-03-29)
        validity=DateRange("2024-01-01", "2025-01-01") if expired
                 else None,
    )


def _override(instructor_id="i1", student_id="s1", verdict="blocked",
              reason="test reason", initiated_by="admin"):
    return InstructorStudentCompatibilityEntity(
        compatibility_id="comp-1",
        instructor_id=instructor_id,
        student_id=student_id,
        verdict=verdict,
        reason=reason,
        initiated_by=initiated_by,
    )


# ── TestCompatibilityCheck ────────────────────────────────────────────────────

class TestCompatibilityCheck(unittest.TestCase):
    """compatibility_service.check() — all three evaluation layers."""

    def _check(self, student=None, instructor=None, credentials=None, overrides=None):
        from backend.app.domain.services import compatibility_service
        return compatibility_service.check(
            student=student or _student(),
            instructor=instructor or _instructor(),
            credentials=credentials or [],
            pair_overrides=overrides or [],
        )

    # ── No constraints → fully compatible ─────────────────────────────────────

    def test_no_overrides_no_restrictions_returns_ok(self):
        result = self._check()
        self.assertTrue(result.can_assign)
        self.assertIsNone(result.hard_verdict)
        self.assertIsNone(result.soft_verdict)
        self.assertEqual(len(result.reasons), 0)

    # ── Pair overrides ─────────────────────────────────────────────────────────

    def test_blocked_override_prevents_assignment(self):
        result = self._check(overrides=[_override(verdict="blocked")])
        self.assertFalse(result.can_assign)
        self.assertTrue(result.is_hard_blocked)

    def test_blocked_override_includes_reason(self):
        result = self._check(overrides=[_override(verdict="blocked", reason="Safeguarding")])
        self.assertIn("Safeguarding", result.reasons[0])

    def test_required_override_allows_assignment(self):
        result = self._check(overrides=[_override(verdict="required")])
        self.assertTrue(result.can_assign)
        self.assertEqual(result.hard_verdict, "required")

    def test_preferred_override_sets_soft_verdict(self):
        result = self._check(overrides=[_override(verdict="preferred")])
        self.assertTrue(result.can_assign)
        self.assertEqual(result.soft_verdict, "preferred")

    def test_disliked_override_sets_soft_verdict(self):
        result = self._check(overrides=[_override(verdict="disliked")])
        self.assertTrue(result.can_assign)
        self.assertEqual(result.soft_verdict, "disliked")

    def test_override_for_different_instructor_is_ignored(self):
        """Override for instructor 'i2' must not affect check for instructor 'i1'."""
        override = _override(instructor_id="i2", verdict="blocked")
        result = self._check(overrides=[override])
        self.assertTrue(result.can_assign)

    def test_override_for_different_student_is_ignored(self):
        override = _override(student_id="s2", verdict="blocked")
        result = self._check(student=_student("s1"), overrides=[override])
        self.assertTrue(result.can_assign)

    def test_blocked_override_returns_immediately_before_other_checks(self):
        """Even if the student has unmet requirements, BLOCKED is returned first."""
        student = _student(requirements=[TeachingRequirement.credential("cpr")])
        instructor = _instructor()
        result = self._check(
            student=student,
            instructor=instructor,
            credentials=[],   # CPR not held
            overrides=[_override(verdict="blocked")],
        )
        self.assertFalse(result.can_assign)
        self.assertTrue(result.is_hard_blocked)

    # ── Instructor age restrictions ────────────────────────────────────────────

    def test_min_age_restriction_met_is_ok(self):
        instructor = _instructor(restrictions=[TeachingRequirement.min_student_age(5)])
        result = self._check(student=_student(age=10), instructor=instructor)
        self.assertTrue(result.can_assign)

    def test_min_age_restriction_violated_blocks(self):
        instructor = _instructor(restrictions=[TeachingRequirement.min_student_age(10)])
        result = self._check(student=_student(age=7), instructor=instructor)
        self.assertFalse(result.can_assign)

    def test_min_age_restriction_exact_boundary_is_ok(self):
        instructor = _instructor(restrictions=[TeachingRequirement.min_student_age(8)])
        result = self._check(student=_student(age=8), instructor=instructor)
        self.assertTrue(result.can_assign)

    def test_max_age_restriction_met_is_ok(self):
        instructor = _instructor(restrictions=[TeachingRequirement.max_student_age(18)])
        result = self._check(student=_student(age=15), instructor=instructor)
        self.assertTrue(result.can_assign)

    def test_max_age_restriction_violated_blocks(self):
        instructor = _instructor(restrictions=[TeachingRequirement.max_student_age(12)])
        result = self._check(student=_student(age=14), instructor=instructor)
        self.assertFalse(result.can_assign)

    def test_max_age_restriction_exact_boundary_is_ok(self):
        instructor = _instructor(restrictions=[TeachingRequirement.max_student_age(18)])
        result = self._check(student=_student(age=18), instructor=instructor)
        self.assertTrue(result.can_assign)

    def test_age_restriction_skipped_when_student_age_is_none(self):
        """If student.age is None, age restrictions are not evaluated."""
        instructor = _instructor(restrictions=[TeachingRequirement.min_student_age(10)])
        result = self._check(student=_student(age=None), instructor=instructor)
        self.assertTrue(result.can_assign)

    # ── Student credential requirements ───────────────────────────────────────

    def test_credential_requirement_met(self):
        student = _student(requirements=[TeachingRequirement.credential("cpr")])
        cred = _credential(instructor_id="i1", credential_type="cpr")
        result = self._check(student=student, credentials=[cred])
        self.assertTrue(result.can_assign)

    def test_credential_requirement_not_met(self):
        student = _student(requirements=[TeachingRequirement.credential("special_ed")])
        result = self._check(student=student, credentials=[])
        self.assertFalse(result.can_assign)

    def test_expired_credential_does_not_satisfy_requirement(self):
        student = _student(requirements=[TeachingRequirement.credential("cpr")])
        expired_cred = _credential(instructor_id="i1", credential_type="cpr", expired=True)
        result = self._check(student=student, credentials=[expired_cred])
        self.assertFalse(result.can_assign)

    def test_credential_for_different_instructor_does_not_satisfy(self):
        """Credentials of instructor 'i2' should not satisfy a requirement for 'i1'."""
        student = _student(requirements=[TeachingRequirement.credential("cpr")])
        cred = _credential(instructor_id="i2", credential_type="cpr")
        result = self._check(
            student=student,
            instructor=_instructor("i1"),
            credentials=[cred],
        )
        self.assertFalse(result.can_assign)

    def test_multiple_credential_requirements_all_must_be_met(self):
        student = _student(requirements=[
            TeachingRequirement.credential("cpr"),
            TeachingRequirement.credential("vulnerable_sector"),
        ])
        only_cpr = _credential(instructor_id="i1", credential_type="cpr")
        result = self._check(student=student, credentials=[only_cpr])
        # vulnerable_sector is missing → should fail
        self.assertFalse(result.can_assign)

    def test_multiple_credential_requirements_all_met(self):
        student = _student(requirements=[
            TeachingRequirement.credential("cpr"),
            TeachingRequirement.credential("vulnerable_sector"),
        ])
        cpr = _credential(instructor_id="i1", credential_type="cpr")
        vs = _credential(instructor_id="i1", credential_type="vulnerable_sector")
        vs = CredentialEntity(
            credential_id="cred-2",
            instructor_id="i1",
            proficiencies=[],
            credential_type="vulnerable_sector",
        )
        result = self._check(student=student, credentials=[cpr, vs])
        self.assertTrue(result.can_assign)

    def test_no_requirements_with_empty_credentials_is_ok(self):
        result = self._check(student=_student(requirements=[]), credentials=[])
        self.assertTrue(result.can_assign)

    def test_requirement_not_met_reason_mentions_credential_type(self):
        student = _student(requirements=[TeachingRequirement.credential("first_aid")])
        result = self._check(student=student, credentials=[])
        self.assertIn("first_aid", result.reasons[0])


# ── TestFilterCompatible ──────────────────────────────────────────────────────

class TestFilterCompatible(unittest.TestCase):
    """compatibility_service.filter_compatible() — filtering and sort order."""

    def _filter(self, student, instructors, credentials=None, overrides=None):
        from backend.app.domain.services import compatibility_service
        return compatibility_service.filter_compatible(
            student=student,
            instructors=instructors,
            credentials=credentials or [],
            pair_overrides=overrides or [],
        )

    def test_returns_empty_when_all_blocked(self):
        student = _student("s1")
        inst = _instructor("i1")
        results = self._filter(
            student, [inst],
            overrides=[_override("i1", "s1", "blocked")],
        )
        self.assertEqual(results, [])

    def test_returns_compatible_instructor(self):
        student = _student()
        inst = _instructor()
        results = self._filter(student, [inst])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].instructor_id, "i1")

    def test_filters_out_blocked_but_keeps_compatible(self):
        student = _student("s1")
        inst_blocked = _instructor("i1")
        inst_ok = _instructor("i2")
        results = self._filter(
            student, [inst_blocked, inst_ok],
            overrides=[_override("i1", "s1", "blocked")],
        )
        ids = [pair[0].instructor_id for pair in results]
        self.assertNotIn("i1", ids)
        self.assertIn("i2", ids)

    def test_required_comes_before_preferred(self):
        student = _student("s1")
        inst_preferred = _instructor("i1")
        inst_required = _instructor("i2")
        overrides = [
            _override("i1", "s1", "preferred"),
            _override("i2", "s1", "required"),
        ]
        results = self._filter(student, [inst_preferred, inst_required], overrides=overrides)
        self.assertEqual(results[0][0].instructor_id, "i2")

    def test_preferred_comes_before_neutral(self):
        student = _student("s1")
        inst_neutral = _instructor("i1")
        inst_preferred = _instructor("i2")
        overrides = [_override("i2", "s1", "preferred")]
        results = self._filter(student, [inst_neutral, inst_preferred], overrides=overrides)
        self.assertEqual(results[0][0].instructor_id, "i2")

    def test_neutral_comes_before_disliked(self):
        student = _student("s1")
        inst_disliked = _instructor("i1")
        inst_neutral = _instructor("i2")
        overrides = [_override("i1", "s1", "disliked")]
        results = self._filter(student, [inst_disliked, inst_neutral], overrides=overrides)
        ids = [pair[0].instructor_id for pair in results]
        self.assertEqual(ids[-1], "i1")  # disliked comes last

    def test_disliked_is_still_included(self):
        """DISLIKED is a soft signal — the instructor is still assignable."""
        student = _student("s1")
        inst = _instructor("i1")
        results = self._filter(
            student, [inst],
            overrides=[_override("i1", "s1", "disliked")],
        )
        self.assertEqual(len(results), 1)

    def test_result_tuples_contain_instructor_and_result(self):
        student = _student()
        inst = _instructor()
        pairs = self._filter(student, [inst])
        self.assertEqual(len(pairs), 1)
        instructor, result = pairs[0]
        self.assertEqual(instructor.instructor_id, "i1")
        self.assertTrue(result.can_assign)

    def test_multiple_instructors_no_constraints_all_returned(self):
        student = _student()
        instructors = [_instructor(f"i{n}") for n in range(1, 6)]
        results = self._filter(student, instructors)
        self.assertEqual(len(results), 5)


if __name__ == "__main__":
    unittest.main()
