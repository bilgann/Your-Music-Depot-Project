"""
Integration tests covering:
  FR-01 — CRUD Instructors
  FR-02 — CRUD Students
  FR-03 — CRUD Rooms
  FR-04 — CRUD Lessons
  FR-05 — CRUD Invoices / Payments
  FR-10 — View Schedule (week filter)
  FR-14 — Search (response fields for filtering)
  FR-16 — Data Validation via API (422 on invalid payloads)
  FR-17 — Referential Integrity via API (409 on FK violations)

All resource endpoints require authentication (NFR-08).
A valid JWT is obtained once at module load and included in every request.
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

# Obtain a test JWT using the dev fallback (barnes / password)
_login_res = _client.post("/user/login?username=barnes&password=password")
_H = {"Authorization": f"Bearer {_login_res.get_json()['data']}"}  # auth headers

_VALID_LESSON = {
    "student_id": "s1", "instructor_id": "i1", "room_id": "r1",
    "start_time": "2025-09-10T10:00:00", "end_time": "2025-09-10T11:00:00",
    "rate": 50.0,
}


# ── FR-01: Instructors ────────────────────────────────────────────────────────

class TestFRCrudInstructors(unittest.TestCase):
    """FR-01: Add, view, update, and delete instructor records."""

    def test_list_instructors_returns_200(self):
        with patch("backend.app.services.instructor.list_instructors", return_value=([], 0)):
            res = _client.get("/api/instructors", headers=_H)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

    def test_unauthenticated_request_returns_401(self):
        """NFR-08/NFR-09: No token → 401."""
        with patch("backend.app.services.instructor.list_instructors", return_value=([], 0)):
            res = _client.get("/api/instructors")
        self.assertEqual(res.status_code, 401)

    def test_get_instructor_returns_200(self):
        data = [{"instructor_id": "i1", "name": "Alice"}]
        with patch("backend.app.services.instructor.get_instructor_by_id", return_value=data):
            res = _client.get("/api/instructors/i1", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_get_instructor_not_found_returns_404(self):
        with patch("backend.app.services.instructor.get_instructor_by_id", return_value=[]):
            res = _client.get("/api/instructors/nobody", headers=_H)
        self.assertEqual(res.status_code, 404)

    def test_create_instructor_returns_201(self):
        created = [{"instructor_id": "i2", "name": "Bob"}]
        with patch("backend.app.services.instructor.create_instructor", return_value=created):
            res = _client.post("/api/instructors", json={"name": "Bob"}, headers=_H)
        self.assertEqual(res.status_code, 201)

    def test_create_instructor_missing_name_returns_422(self):
        res = _client.post("/api/instructors", json={}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_create_instructor_wrong_email_type_returns_422(self):
        res = _client.post("/api/instructors", json={"name": "Bob", "email": 123}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_update_instructor_returns_200(self):
        with patch("backend.app.services.instructor.update_instructor", return_value=[]):
            res = _client.put("/api/instructors/i1", json={"email": "a@new.com"}, headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_delete_instructor_returns_200(self):
        with patch("backend.app.services.instructor.delete_instructor", return_value=[]):
            res = _client.delete("/api/instructors/i1", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_delete_instructor_with_lessons_returns_409(self):
        """FR-17: Cannot delete instructor referenced by lessons."""
        with patch(
            "backend.app.services.instructor.delete_instructor",
            side_effect=Exception("ERROR: 23503 foreign key violation"),
        ):
            res = _client.delete("/api/instructors/i1", headers=_H)
        self.assertEqual(res.status_code, 409)


# ── FR-02: Students ───────────────────────────────────────────────────────────

class TestFRCrudStudents(unittest.TestCase):
    """FR-02: Add, view, update, and delete student records."""

    def test_list_students_returns_200(self):
        with patch("backend.app.services.student.list_students", return_value=([], 0)):
            res = _client.get("/api/students", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_unauthenticated_request_returns_401(self):
        """NFR-09: Personal student data requires a valid session."""
        res = _client.get("/api/students")
        self.assertEqual(res.status_code, 401)

    def test_get_student_returns_200(self):
        data = [{"student_id": "s1", "name": "Carol"}]
        with patch("backend.app.services.student.get_student_by_id", return_value=data):
            res = _client.get("/api/students/s1", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_get_student_not_found_returns_404(self):
        with patch("backend.app.services.student.get_student_by_id", return_value=[]):
            res = _client.get("/api/students/nobody", headers=_H)
        self.assertEqual(res.status_code, 404)

    def test_create_student_returns_201(self):
        with patch("backend.app.services.student.create_student", return_value=[{"student_id": "s2"}]):
            res = _client.post("/api/students", json={"name": "Dan", "client_id": "c1"}, headers=_H)
        self.assertEqual(res.status_code, 201)

    def test_create_student_missing_name_returns_422(self):
        res = _client.post("/api/students", json={}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_update_student_returns_200(self):
        with patch("backend.app.services.student.update_student", return_value=[]):
            res = _client.put("/api/students/s1", json={"phone": "555-0199"}, headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_delete_student_returns_200(self):
        with patch("backend.app.services.student.delete_student", return_value=[]):
            res = _client.delete("/api/students/s1", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_delete_student_with_bookings_returns_409(self):
        """FR-17: Cannot delete student who has lesson records."""
        with patch(
            "backend.app.services.student.delete_student",
            side_effect=Exception("ERROR: 23503 foreign key violation"),
        ):
            res = _client.delete("/api/students/s1", headers=_H)
        self.assertEqual(res.status_code, 409)


# ── FR-03: Rooms ──────────────────────────────────────────────────────────────

class TestFRCrudRooms(unittest.TestCase):
    """FR-03: Manage room inventory with capacity and instrument type."""

    def test_list_rooms_returns_200(self):
        with patch("backend.app.services.room.list_rooms", return_value=([], 0)):
            res = _client.get("/api/rooms", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_get_room_returns_200(self):
        data = [{"room_id": "r1", "name": "Room A", "capacity": 5}]
        with patch("backend.app.services.room.get_room_by_id", return_value=data):
            res = _client.get("/api/rooms/r1", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_get_room_not_found_returns_404(self):
        with patch("backend.app.services.room.get_room_by_id", return_value=[]):
            res = _client.get("/api/rooms/nobody", headers=_H)
        self.assertEqual(res.status_code, 404)

    def test_create_room_returns_201(self):
        with patch("backend.app.services.room.create_room", return_value=[{"room_id": "r2"}]):
            res = _client.post("/api/rooms", json={"name": "Room B", "capacity": 4}, headers=_H)
        self.assertEqual(res.status_code, 201)

    def test_create_room_missing_name_returns_422(self):
        res = _client.post("/api/rooms", json={}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_create_room_capacity_must_be_int(self):
        res = _client.post("/api/rooms", json={"name": "Room C", "capacity": "big"}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_update_room_returns_200(self):
        with patch("backend.app.services.room.update_room", return_value=[]):
            res = _client.put("/api/rooms/r1", json={"capacity": 8}, headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_delete_room_returns_200(self):
        with patch("backend.app.services.room.delete_room", return_value=[]):
            res = _client.delete("/api/rooms/r1", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_delete_room_with_lessons_returns_409(self):
        with patch(
            "backend.app.services.room.delete_room",
            side_effect=Exception("ERROR: 23503 foreign key violation"),
        ):
            res = _client.delete("/api/rooms/r1", headers=_H)
        self.assertEqual(res.status_code, 409)


# ── FR-04: Lessons ────────────────────────────────────────────────────────────

class TestFRCrudLessons(unittest.TestCase):
    """FR-04: Create, modify, and cancel lessons; FR-10: schedule view."""

    def test_list_lessons_returns_200(self):
        with patch("backend.app.services.lesson.get_all_lessons", return_value=[]):
            res = _client.get("/api/lessons", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_list_lessons_by_week_uses_filter(self):
        """FR-10: weekStart + weekEnd invoke week-scoped query."""
        with patch("backend.app.services.lesson.get_lessons_for_week", return_value=[]) as svc:
            res = _client.get("/api/lessons?weekStart=2025-09-08&weekEnd=2025-09-14", headers=_H)
        self.assertEqual(res.status_code, 200)
        svc.assert_called_once_with("2025-09-08", "2025-09-14")

    def test_get_lesson_returns_200(self):
        data = [{"lesson_id": "l1", **_VALID_LESSON}]
        with patch("backend.app.services.lesson.get_lesson_by_id", return_value=data):
            res = _client.get("/api/lessons/l1", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_get_lesson_not_found_returns_404(self):
        with patch("backend.app.services.lesson.get_lesson_by_id", return_value=[]):
            res = _client.get("/api/lessons/nobody", headers=_H)
        self.assertEqual(res.status_code, 404)

    def test_create_lesson_returns_201(self):
        with patch("backend.app.services.lesson.create_lesson", return_value=[{"lesson_id": "l2"}]):
            res = _client.post("/api/lessons", json=_VALID_LESSON, headers=_H)
        self.assertEqual(res.status_code, 201)

    def test_create_lesson_missing_fields_returns_422(self):
        res = _client.post("/api/lessons", json={}, headers=_H)
        self.assertEqual(res.status_code, 422)
        fields = [e["field"] for e in res.get_json().get("errors", [])]
        for f in ("instructor_id", "room_id", "start_time", "end_time"):
            self.assertIn(f, fields)

    def test_create_lesson_invalid_rate_type_returns_422(self):
        res = _client.post("/api/lessons", json={**_VALID_LESSON, "rate": "fifty"}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_update_lesson_returns_200(self):
        with patch("backend.app.services.lesson.update_lesson", return_value=[]):
            res = _client.put("/api/lessons/l1", json={"rate": 60.0}, headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_delete_lesson_returns_200(self):
        with patch("backend.app.services.lesson.delete_lesson", return_value=[]):
            res = _client.delete("/api/lessons/l1", headers=_H)
        self.assertEqual(res.status_code, 200)


# ── FR-05: Invoices ───────────────────────────────────────────────────────────

class TestFRCrudInvoices(unittest.TestCase):
    """FR-05: Generate and manage billing documents — admin access only."""

    def test_list_invoices_returns_200_for_admin(self):
        with patch("backend.app.services.invoice.get_all_invoices", return_value=[]):
            res = _client.get("/api/invoices", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_invoices_blocked_without_token(self):
        """NFR-08: Financial data requires authentication."""
        res = _client.get("/api/invoices")
        self.assertEqual(res.status_code, 401)

    def test_get_invoice_returns_200(self):
        data = [{"invoice_id": "inv1", "student_id": "s1", "total_amount": 100.0}]
        with patch("backend.app.services.invoice.get_invoice_by_id", return_value=data):
            res = _client.get("/api/invoices/inv1", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_get_invoice_not_found_returns_404(self):
        with patch("backend.app.services.invoice.get_invoice_by_id", return_value=[]):
            res = _client.get("/api/invoices/nobody", headers=_H)
        self.assertEqual(res.status_code, 404)

    def test_create_invoice_returns_201(self):
        with patch("backend.app.services.invoice.create_invoice", return_value=[{"invoice_id": "inv2"}]):
            res = _client.post("/api/invoices", json={"student_id": "s1", "total_amount": 150.0}, headers=_H)
        self.assertEqual(res.status_code, 201)

    def test_create_invoice_missing_fields_returns_422(self):
        res = _client.post("/api/invoices", json={}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_update_invoice_returns_200(self):
        with patch("backend.app.services.invoice.update_invoice", return_value=[]):
            res = _client.put("/api/invoices/inv1", json={"status": "Paid"}, headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_delete_invoice_returns_200(self):
        with patch("backend.app.services.invoice.delete_invoice", return_value=[]):
            res = _client.delete("/api/invoices/inv1", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_get_line_items_returns_200(self):
        lines = [{"invoice_id": "inv1", "lesson_id": "l1", "amount": 50.0}]
        with patch("backend.app.services.invoice.get_line_items", return_value=lines):
            res = _client.get("/api/invoices/inv1/line-items", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_outstanding_balance_returns_200(self):
        balance = {"invoices": [], "total_outstanding_balance": 0.0}
        with patch("backend.app.services.invoice.get_outstanding_balance", return_value=balance):
            res = _client.get("/api/invoices/outstanding-balance", headers=_H)
        self.assertEqual(res.status_code, 200)


# ── FR-05: Payments ───────────────────────────────────────────────────────────

class TestFRCrudPayments(unittest.TestCase):
    """FR-05 / FR-12: Record and view payment transactions — admin access only."""

    def test_list_payments_returns_200_for_admin(self):
        with patch("backend.app.services.payment.list_payments", return_value=([], 0)):
            res = _client.get("/api/payments", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_payments_blocked_without_token(self):
        """NFR-08: Payment data requires authentication."""
        res = _client.get("/api/payments")
        self.assertEqual(res.status_code, 401)

    def test_get_payment_returns_200(self):
        data = [{"payment_id": "p1", "invoice_id": "inv1", "amount": 50.0}]
        with patch("backend.app.services.payment.get_payment_by_id", return_value=data):
            res = _client.get("/api/payments/p1", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_get_payment_not_found_returns_404(self):
        with patch("backend.app.services.payment.get_payment_by_id", return_value=[]):
            res = _client.get("/api/payments/nobody", headers=_H)
        self.assertEqual(res.status_code, 404)

    def test_record_payment_returns_201(self):
        result = {"payment_id": "p2", "invoice_id": "inv1", "amount": 100.0}
        with patch("backend.app.services.payment.record_payment", return_value=result):
            res = _client.post("/api/payments", json={"invoice_id": "inv1", "amount": 100.0}, headers=_H)
        self.assertEqual(res.status_code, 201)

    def test_record_payment_missing_fields_returns_422(self):
        res = _client.post("/api/payments", json={}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_delete_payment_returns_200(self):
        with patch("backend.app.services.payment.delete_payment", return_value=[]):
            res = _client.delete("/api/payments/p1", headers=_H)
        self.assertEqual(res.status_code, 200)


# ── FR-14: Response fields for search and filtering ───────────────────────────

class TestFRSearchableFields(unittest.TestCase):
    """FR-14: API responses expose fields needed for name/keyword search."""

    def test_student_record_exposes_name(self):
        data = [{"student_id": "s1", "name": "Alice"}]
        with patch("backend.app.services.student.list_students", return_value=(data, 1)):
            res = _client.get("/api/students", headers=_H)
        self.assertIn("name", res.get_json()["data"][0])

    def test_instructor_record_exposes_name(self):
        data = [{"instructor_id": "i1", "name": "Bob"}]
        with patch("backend.app.services.instructor.list_instructors", return_value=(data, 1)):
            res = _client.get("/api/instructors", headers=_H)
        self.assertIn("name", res.get_json()["data"][0])

    def test_lesson_record_exposes_ids_for_filtering(self):
        """FR-10, FR-14: Lessons expose student_id, instructor_id, start_time."""
        data = [{"lesson_id": "l1", "student_id": "s1", "instructor_id": "i1",
                 "room_id": "r1", "start_time": "2025-09-10T10:00:00"}]
        with patch("backend.app.services.lesson.get_all_lessons", return_value=data):
            res = _client.get("/api/lessons", headers=_H)
        record = res.get_json()["data"][0]
        for field in ("student_id", "instructor_id", "start_time"):
            self.assertIn(field, record)


if __name__ == "__main__":
    unittest.main()
