"""
Integration tests covering:
  FR-06  — Schedule Validation: double-booking surfaces as 409
  FR-07  — Availability Check (not yet implemented — skipped)
  FR-08  — Instructor-Instrument Match (not yet implemented — skipped)
  FR-09  — Recurring Lessons (not yet implemented — skipped)
  FR-11  — Invoice Generation via POST /api/invoices/generate
  FR-13  — Skill-Level Matching (not yet implemented — skipped)
  FR-15  — Conflict Alert: 409 response with a non-empty message
"""
import unittest
from unittest.mock import MagicMock, patch

from backend.app.application.singletons import Auth
from backend.app.application.singletons.database import DatabaseConnection


def _build():
    DatabaseConnection._instance = MagicMock()
    Auth._instance = None
    from backend import build_app
    app = build_app()
    app.config["TESTING"] = True
    return app.test_client()


_client = _build()
_login_res = _client.post("/user/login?username=barnes&password=password")
_H = {"Authorization": f"Bearer {_login_res.get_json()['data']}"}

_VALID_LESSON = {
    "student_id": "s1", "instructor_id": "i1", "room_id": "r1",
    "start_time": "2025-09-10T10:00:00", "end_time": "2025-09-10T11:00:00",
    "rate": 50.0,
}


# ── FR-06 + FR-15: Conflict detection ────────────────────────────────────────

class TestFRScheduleConflict(unittest.TestCase):
    """FR-06, FR-15: DB constraint violations are translated to 409 with a message."""

    def test_unique_constraint_violation_returns_409(self):
        with patch(
            "backend.app.services.lesson.create_lesson",
            side_effect=Exception("ERROR: 23505 unique constraint violated"),
        ):
            res = _client.post("/api/lessons", json=_VALID_LESSON, headers=_H)
        self.assertEqual(res.status_code, 409)

    def test_conflict_response_has_non_empty_message(self):
        """FR-15: The conflict warning message is present and non-empty."""
        with patch(
            "backend.app.services.lesson.create_lesson",
            side_effect=Exception("duplicate key value violates unique constraint"),
        ):
            res = _client.post("/api/lessons", json=_VALID_LESSON, headers=_H)
        body = res.get_json()
        self.assertEqual(res.status_code, 409)
        self.assertFalse(body["success"])
        self.assertTrue(len(body.get("message", "")) > 0)

    def test_fk_violation_on_create_returns_409(self):
        with patch(
            "backend.app.services.lesson.create_lesson",
            side_effect=Exception("ERROR: 23503 foreign key violation"),
        ):
            res = _client.post("/api/lessons", json=_VALID_LESSON, headers=_H)
        self.assertEqual(res.status_code, 409)

    def test_delete_instructor_with_lessons_returns_409_with_message(self):
        """FR-17, FR-15: Delete constraint alert returns 409 with a message."""
        with patch(
            "backend.app.services.instructor.delete_instructor",
            side_effect=Exception("ERROR: 23503 foreign key violation on lesson"),
        ):
            res = _client.delete("/api/instructors/i1", headers=_H)
        body = res.get_json()
        self.assertEqual(res.status_code, 409)
        self.assertIsNotNone(body.get("message"))


# ── FR-11: Invoice Generation via API ────────────────────────────────────────

class TestFRInvoiceGenerationAPI(unittest.TestCase):
    """FR-11: Generate monthly invoices via POST /api/invoices/generate."""

    def test_generate_invoice_returns_201(self):
        mock_result = {
            "invoice": {"invoice_id": "inv-1", "total_amount": 100.0, "status": "Pending"},
            "line_items": [{"lesson_id": "l1", "amount": 100.0}],
        }
        with patch("backend.app.services.invoice.generate_monthly_invoice", return_value=mock_result):
            res = _client.post(
                "/api/invoices/generate",
                json={"student_id": "s1", "year": 2025, "month": 9},
                headers=_H,
            )
        self.assertEqual(res.status_code, 201)
        body = res.get_json()
        self.assertTrue(body["success"])
        self.assertIn("invoice", body["data"])
        self.assertIn("line_items", body["data"])

    def test_generate_invoice_requires_auth(self):
        """Financial endpoints require a valid session."""
        res = _client.post("/api/invoices/generate", json={"student_id": "s1", "year": 2025, "month": 9})
        self.assertEqual(res.status_code, 401)

    def test_generate_invoice_missing_student_id_returns_422(self):
        res = _client.post("/api/invoices/generate", json={"year": 2025, "month": 9}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_generate_invoice_missing_year_returns_422(self):
        res = _client.post("/api/invoices/generate", json={"student_id": "s1", "month": 9}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_generate_invoice_missing_month_returns_422(self):
        res = _client.post("/api/invoices/generate", json={"student_id": "s1", "year": 2025}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_generate_invoice_duplicate_returns_error(self):
        with patch(
            "backend.app.services.invoice.generate_monthly_invoice",
            side_effect=ValueError("Invoice for student s1 covering 2025-09-01 already exists."),
        ):
            res = _client.post(
                "/api/invoices/generate",
                json={"student_id": "s1", "year": 2025, "month": 9},
                headers=_H,
            )
        self.assertFalse(res.get_json()["success"])

    def test_generated_invoice_response_contains_line_items(self):
        mock_result = {
            "invoice": {"invoice_id": "inv-1", "total_amount": 150.0},
            "line_items": [{"lesson_id": f"l{i}", "amount": 50.0} for i in range(3)],
        }
        with patch("backend.app.services.invoice.generate_monthly_invoice", return_value=mock_result):
            res = _client.post(
                "/api/invoices/generate",
                json={"student_id": "s1", "year": 2025, "month": 9},
                headers=_H,
            )
        self.assertEqual(len(res.get_json()["data"]["line_items"]), 3)


# ── FR-07: Availability Check (not yet implemented) ───────────────────────────

class TestFRAvailabilityCheck(unittest.TestCase):
    @unittest.skip("FR-07 not yet implemented: availability check not integrated into lesson creation")
    def test_lesson_outside_availability_returns_409(self):
        res = _client.post("/api/lessons", json=_VALID_LESSON, headers=_H)
        self.assertEqual(res.status_code, 409)


# ── FR-08: Instructor-Instrument Match (not yet implemented) ──────────────────

class TestFRInstrumentMatch(unittest.TestCase):
    @unittest.skip("FR-08 not yet implemented: skill_matching.py service is empty")
    def test_unqualified_instrument_booking_returns_409(self):
        res = _client.post("/api/lessons", json={**_VALID_LESSON, "instrument": "violin"}, headers=_H)
        self.assertEqual(res.status_code, 409)


# ── FR-09: Recurring Lessons (not yet implemented) ───────────────────────────

class TestFRRecurringLessons(unittest.TestCase):
    @unittest.skip("FR-09 not yet implemented: no recurring lesson endpoint exists")
    def test_recurring_lesson_creates_one_per_week(self):
        payload = {**_VALID_LESSON, "recurrence": "weekly",
                   "term_start": "2025-09-08", "term_end": "2026-06-27"}
        res = _client.post("/api/lessons/recurring", json=payload, headers=_H)
        self.assertEqual(res.status_code, 201)
        self.assertGreaterEqual(len(res.get_json()["data"]), 39)


# ── FR-13: Skill-Level Matching (not yet implemented) ────────────────────────

class TestFRSkillLevelMatching(unittest.TestCase):
    @unittest.skip("FR-13 not yet implemented: skill_matching.py service is empty")
    def test_instructor_below_student_skill_level_is_rejected(self):
        res = _client.post("/api/lessons", json={**_VALID_LESSON, "student_skill_level": "advanced"}, headers=_H)
        self.assertEqual(res.status_code, 409)


if __name__ == "__main__":
    unittest.main()
