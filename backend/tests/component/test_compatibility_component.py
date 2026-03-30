"""
Component tests for the compatibility application service.

Tests the full stack down to (but not including) the infrastructure layer:
  application/services/compatibility.py

The infrastructure repositories are patched so no real DB connection is needed.

Covers:
  check_compatibility()          — student/instructor not found, successful check
  filter_compatible_instructors() — student not found, ranking, empty list
"""
import unittest
from unittest.mock import MagicMock, patch

from backend.app.domain.exceptions.exceptions import NotFoundError
from backend.app.infrastructure.database.database import DatabaseConnection


def _mock_db():
    inst = MagicMock()
    DatabaseConnection._instance = inst
    return inst


# ── check_compatibility ───────────────────────────────────────────────────────

class TestCheckCompatibility(unittest.TestCase):

    def setUp(self):
        _mock_db()

    def tearDown(self):
        DatabaseConnection._instance = None

    def test_student_not_found_raises_not_found(self):
        with patch("backend.app.application.services.compatibility.Student") as mock_s:
            mock_s.get.return_value = []
            from backend.app.application.services.compatibility import check_compatibility
            with self.assertRaises(NotFoundError):
                check_compatibility("s999", "i1")

    def test_instructor_not_found_raises_not_found(self):
        with patch("backend.app.application.services.compatibility.Student") as mock_s, \
             patch("backend.app.application.services.compatibility.Instructor") as mock_i:
            mock_s.get.return_value = [{"student_id": "s1", "person_id": "p1"}]
            mock_i.get.return_value = []
            from backend.app.application.services.compatibility import check_compatibility
            with self.assertRaises(NotFoundError):
                check_compatibility("s1", "i999")

    def test_compatible_pair_returns_can_assign_true(self):
        student_row = {"student_id": "s1", "person_id": "p1"}
        instructor_row = {"instructor_id": "i1", "person_id": "p2"}
        with patch("backend.app.application.services.compatibility.Student") as mock_s, \
             patch("backend.app.application.services.compatibility.Instructor") as mock_i, \
             patch("backend.app.application.services.compatibility.Credential") as mock_c, \
             patch("backend.app.application.services.compatibility.InstructorStudentCompatibility") as mock_compat:
            mock_s.get.return_value = [student_row]
            mock_i.get.return_value = [instructor_row]
            mock_c.get_by_instructor.return_value = []
            mock_compat.get.return_value = []
            from backend.app.application.services.compatibility import check_compatibility
            result = check_compatibility("s1", "i1")
        self.assertTrue(result["can_assign"])

    def test_result_contains_expected_keys(self):
        student_row = {"student_id": "s1", "person_id": "p1"}
        instructor_row = {"instructor_id": "i1", "person_id": "p2"}
        with patch("backend.app.application.services.compatibility.Student") as mock_s, \
             patch("backend.app.application.services.compatibility.Instructor") as mock_i, \
             patch("backend.app.application.services.compatibility.Credential") as mock_c, \
             patch("backend.app.application.services.compatibility.InstructorStudentCompatibility") as mock_compat:
            mock_s.get.return_value = [student_row]
            mock_i.get.return_value = [instructor_row]
            mock_c.get_by_instructor.return_value = []
            mock_compat.get.return_value = []
            from backend.app.application.services.compatibility import check_compatibility
            result = check_compatibility("s1", "i1")
        for key in ("can_assign", "hard_verdict", "soft_verdict", "reasons"):
            self.assertIn(key, result)

    def test_blocked_pair_returns_can_assign_false(self):
        student_row = {"student_id": "s1", "person_id": "p1"}
        instructor_row = {"instructor_id": "i1", "person_id": "p2"}
        blocked_override = {
            "compatibility_id": "c1",
            "instructor_id": "i1",
            "student_id": "s1",
            "verdict": "blocked",
            "reason": "safeguarding",
            "initiated_by": "admin",
        }
        with patch("backend.app.application.services.compatibility.Student") as mock_s, \
             patch("backend.app.application.services.compatibility.Instructor") as mock_i, \
             patch("backend.app.application.services.compatibility.Credential") as mock_c, \
             patch("backend.app.application.services.compatibility.InstructorStudentCompatibility") as mock_compat:
            mock_s.get.return_value = [student_row]
            mock_i.get.return_value = [instructor_row]
            mock_c.get_by_instructor.return_value = []
            mock_compat.get.return_value = [blocked_override]
            from backend.app.application.services.compatibility import check_compatibility
            result = check_compatibility("s1", "i1")
        self.assertFalse(result["can_assign"])
        self.assertEqual(result["hard_verdict"], "blocked")

    def test_credential_requirement_met_returns_can_assign_true(self):
        student_row = {
            "student_id": "s1", "person_id": "p1",
            "requirements": [{"requirement_type": "credential", "value": "cpr"}],
        }
        instructor_row = {"instructor_id": "i1", "person_id": "p2"}
        cpr_credential = {
            "credential_id": "cred-1",
            "instructor_id": "i1",
            "proficiencies": [],
            "credential_type": "cpr",
        }
        with patch("backend.app.application.services.compatibility.Student") as mock_s, \
             patch("backend.app.application.services.compatibility.Instructor") as mock_i, \
             patch("backend.app.application.services.compatibility.Credential") as mock_c, \
             patch("backend.app.application.services.compatibility.InstructorStudentCompatibility") as mock_compat:
            mock_s.get.return_value = [student_row]
            mock_i.get.return_value = [instructor_row]
            mock_c.get_by_instructor.return_value = [cpr_credential]
            mock_compat.get.return_value = []
            from backend.app.application.services.compatibility import check_compatibility
            result = check_compatibility("s1", "i1")
        self.assertTrue(result["can_assign"])

    def test_unmet_credential_requirement_returns_can_assign_false(self):
        student_row = {
            "student_id": "s1", "person_id": "p1",
            "requirements": [{"requirement_type": "credential", "value": "special_ed"}],
        }
        instructor_row = {"instructor_id": "i1", "person_id": "p2"}
        with patch("backend.app.application.services.compatibility.Student") as mock_s, \
             patch("backend.app.application.services.compatibility.Instructor") as mock_i, \
             patch("backend.app.application.services.compatibility.Credential") as mock_c, \
             patch("backend.app.application.services.compatibility.InstructorStudentCompatibility") as mock_compat:
            mock_s.get.return_value = [student_row]
            mock_i.get.return_value = [instructor_row]
            mock_c.get_by_instructor.return_value = []  # no credentials
            mock_compat.get.return_value = []
            from backend.app.application.services.compatibility import check_compatibility
            result = check_compatibility("s1", "i1")
        self.assertFalse(result["can_assign"])

    def test_reasons_is_a_list(self):
        student_row = {"student_id": "s1", "person_id": "p1"}
        instructor_row = {"instructor_id": "i1", "person_id": "p2"}
        with patch("backend.app.application.services.compatibility.Student") as mock_s, \
             patch("backend.app.application.services.compatibility.Instructor") as mock_i, \
             patch("backend.app.application.services.compatibility.Credential") as mock_c, \
             patch("backend.app.application.services.compatibility.InstructorStudentCompatibility") as mock_compat:
            mock_s.get.return_value = [student_row]
            mock_i.get.return_value = [instructor_row]
            mock_c.get_by_instructor.return_value = []
            mock_compat.get.return_value = []
            from backend.app.application.services.compatibility import check_compatibility
            result = check_compatibility("s1", "i1")
        self.assertIsInstance(result["reasons"], list)


# ── filter_compatible_instructors ─────────────────────────────────────────────

class TestFilterCompatibleInstructors(unittest.TestCase):

    def setUp(self):
        _mock_db()

    def tearDown(self):
        DatabaseConnection._instance = None

    def test_student_not_found_raises_not_found(self):
        with patch("backend.app.application.services.compatibility.Student") as mock_s:
            mock_s.get.return_value = []
            from backend.app.application.services.compatibility import filter_compatible_instructors
            with self.assertRaises(NotFoundError):
                filter_compatible_instructors("s999")

    def test_no_instructors_returns_empty_list(self):
        student_row = {"student_id": "s1", "person_id": "p1"}
        with patch("backend.app.application.services.compatibility.Student") as mock_s, \
             patch("backend.app.application.services.compatibility.Instructor") as mock_i, \
             patch("backend.app.application.services.compatibility.Credential") as mock_c, \
             patch("backend.app.application.services.compatibility.InstructorStudentCompatibility") as mock_compat:
            mock_s.get.return_value = [student_row]
            mock_i.get_all.return_value = []
            mock_c.get_all.return_value = []
            mock_compat.get_by_student.return_value = []
            from backend.app.application.services.compatibility import filter_compatible_instructors
            result = filter_compatible_instructors("s1")
        self.assertEqual(result, [])

    def test_compatible_instructors_are_returned(self):
        student_row = {"student_id": "s1", "person_id": "p1"}
        instructor_rows = [
            {"instructor_id": "i1", "person_id": "p2"},
            {"instructor_id": "i2", "person_id": "p3"},
        ]
        with patch("backend.app.application.services.compatibility.Student") as mock_s, \
             patch("backend.app.application.services.compatibility.Instructor") as mock_i, \
             patch("backend.app.application.services.compatibility.Credential") as mock_c, \
             patch("backend.app.application.services.compatibility.InstructorStudentCompatibility") as mock_compat:
            mock_s.get.return_value = [student_row]
            mock_i.get_all.return_value = instructor_rows
            mock_c.get_all.return_value = []
            mock_compat.get_by_student.return_value = []
            from backend.app.application.services.compatibility import filter_compatible_instructors
            result = filter_compatible_instructors("s1")
        self.assertEqual(len(result), 2)

    def test_blocked_instructor_excluded(self):
        student_row = {"student_id": "s1", "person_id": "p1"}
        instructor_rows = [
            {"instructor_id": "i1", "person_id": "p2"},
        ]
        blocked_override = {
            "compatibility_id": "c1",
            "instructor_id": "i1",
            "student_id": "s1",
            "verdict": "blocked",
            "reason": "conflict",
            "initiated_by": "admin",
        }
        with patch("backend.app.application.services.compatibility.Student") as mock_s, \
             patch("backend.app.application.services.compatibility.Instructor") as mock_i, \
             patch("backend.app.application.services.compatibility.Credential") as mock_c, \
             patch("backend.app.application.services.compatibility.InstructorStudentCompatibility") as mock_compat:
            mock_s.get.return_value = [student_row]
            mock_i.get_all.return_value = instructor_rows
            mock_c.get_all.return_value = []
            mock_compat.get_by_student.return_value = [blocked_override]
            from backend.app.application.services.compatibility import filter_compatible_instructors
            result = filter_compatible_instructors("s1")
        self.assertEqual(result, [])

    def test_result_dicts_contain_instructor_id(self):
        student_row = {"student_id": "s1", "person_id": "p1"}
        instructor_rows = [{"instructor_id": "i1", "person_id": "p2"}]
        with patch("backend.app.application.services.compatibility.Student") as mock_s, \
             patch("backend.app.application.services.compatibility.Instructor") as mock_i, \
             patch("backend.app.application.services.compatibility.Credential") as mock_c, \
             patch("backend.app.application.services.compatibility.InstructorStudentCompatibility") as mock_compat:
            mock_s.get.return_value = [student_row]
            mock_i.get_all.return_value = instructor_rows
            mock_c.get_all.return_value = []
            mock_compat.get_by_student.return_value = []
            from backend.app.application.services.compatibility import filter_compatible_instructors
            result = filter_compatible_instructors("s1")
        self.assertIn("instructor_id", result[0])

    def test_required_instructor_comes_first(self):
        student_row = {"student_id": "s1", "person_id": "p1"}
        instructor_rows = [
            {"instructor_id": "i1", "person_id": "p2"},
            {"instructor_id": "i2", "person_id": "p3"},
        ]
        overrides = [
            {
                "compatibility_id": "c1", "instructor_id": "i2", "student_id": "s1",
                "verdict": "required", "reason": "student request", "initiated_by": "student",
            }
        ]
        with patch("backend.app.application.services.compatibility.Student") as mock_s, \
             patch("backend.app.application.services.compatibility.Instructor") as mock_i, \
             patch("backend.app.application.services.compatibility.Credential") as mock_c, \
             patch("backend.app.application.services.compatibility.InstructorStudentCompatibility") as mock_compat:
            mock_s.get.return_value = [student_row]
            mock_i.get_all.return_value = instructor_rows
            mock_c.get_all.return_value = []
            mock_compat.get_by_student.return_value = overrides
            from backend.app.application.services.compatibility import filter_compatible_instructors
            result = filter_compatible_instructors("s1")
        self.assertEqual(result[0]["instructor_id"], "i2")
        self.assertEqual(result[0]["hard_verdict"], "required")


if __name__ == "__main__":
    unittest.main()
