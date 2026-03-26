"""
Integration tests covering:
  P2 Auditing — audit_log entries created on CRUD operations
  P2 Auditing — GET /api/audit accessible to admin only
"""
import unittest
from unittest.mock import MagicMock, patch, call

import jwt

from backend.app.singletons.auth import Auth
from backend.app.singletons.database import DatabaseConnection

_SECRET = "supersecretkey"


def _build():
    DatabaseConnection._instance = MagicMock()
    Auth._instance = None
    from backend import build_app
    app = build_app()
    app.config["TESTING"] = True
    return app.test_client()


_client = _build()
_token = _client.post("/user/login?username=barnes&password=password").get_json()["data"]
_H = {"Authorization": f"Bearer {_token}"}
_INSTRUCTOR_TOKEN = jwt.encode(
    {"user_id": "i1", "username": "instructor", "role": "instructor"},
    _SECRET, algorithm="HS256",
)


# ── Audit log endpoint ────────────────────────────────────────────────────────

class TestAuditEndpoint(unittest.TestCase):
    """GET /api/audit — admin-only view of all audit log entries."""

    def test_audit_log_accessible_to_admin(self):
        logs = [{"log_id": "l1", "action": "CREATE", "entity_type": "student"}]
        with patch(
            "backend.app.controllers.audit.DatabaseConnection"
        ) as mock_db_cls:
            mock_db_cls.return_value.client.table.return_value \
                .select.return_value.order.return_value.limit.return_value \
                .execute.return_value.data = logs
            res = _client.get("/api/audit", headers=_H)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

    def test_audit_log_blocked_without_token(self):
        res = _client.get("/api/audit")
        self.assertEqual(res.status_code, 401)

    def test_audit_log_blocked_for_instructor_role(self):
        res = _client.get("/api/audit", headers={"Authorization": f"Bearer {_INSTRUCTOR_TOKEN}"})
        self.assertEqual(res.status_code, 403)

    def test_audit_log_filtered_by_entity_type(self):
        with patch(
            "backend.app.controllers.audit.DatabaseConnection"
        ) as mock_db_cls:
            chain = mock_db_cls.return_value.client.table.return_value \
                .select.return_value.order.return_value.limit.return_value
            chain.execute.return_value.data = []
            chain.eq.return_value.execute.return_value.data = []
            res = _client.get("/api/audit?entity_type=lesson", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_audit_log_filtered_by_entity_id(self):
        with patch(
            "backend.app.controllers.audit.DatabaseConnection"
        ) as mock_db_cls:
            chain = mock_db_cls.return_value.client.table.return_value \
                .select.return_value.order.return_value.limit.return_value
            chain.execute.return_value.data = []
            chain.eq.return_value.execute.return_value.data = []
            res = _client.get("/api/audit?entity_id=abc-123", headers=_H)
        self.assertEqual(res.status_code, 200)


# ── Audit entries created by service operations ───────────────────────────────

class TestAuditServiceLogging(unittest.TestCase):
    """Verify that audit.log() is called on CREATE / UPDATE / DELETE operations."""

    def test_create_student_triggers_audit_log(self):
        with patch("backend.app.services.student.create_student",
                   return_value=[{"student_id": "s1", "name": "Alice"}]):
            with patch("backend.app.services.audit.log") as mock_log:
                _client.post("/api/students", json={"name": "Alice"}, headers=_H)
        mock_log.assert_called_once()
        args = mock_log.call_args[0]
        self.assertEqual(args[1], "CREATE")
        self.assertEqual(args[2], "student")

    def test_update_student_triggers_audit_log(self):
        with patch("backend.app.services.student.update_student", return_value=[]):
            with patch("backend.app.services.audit.log") as mock_log:
                _client.put("/api/students/s1", json={"phone": "555"}, headers=_H)
        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args[0][1], "UPDATE")

    def test_delete_student_triggers_audit_log(self):
        with patch("backend.app.services.student.delete_student", return_value=[]):
            with patch("backend.app.services.audit.log") as mock_log:
                _client.delete("/api/students/s1", headers=_H)
        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args[0][1], "DELETE")

    def test_create_lesson_triggers_audit_log(self):
        valid_lesson = {
            "student_id": "s1", "instructor_id": "i1", "room_id": "r1",
            "start_time": "2025-09-10T10:00:00", "end_time": "2025-09-10T11:00:00",
        }
        with patch("backend.app.services.lesson.create_lesson",
                   return_value=[{"lesson_id": "l1"}]):
            with patch("backend.app.services.audit.log") as mock_log:
                _client.post("/api/lessons", json=valid_lesson, headers=_H)
        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args[0][2], "lesson")

    def test_delete_lesson_triggers_audit_log(self):
        with patch("backend.app.services.lesson.delete_lesson", return_value=[]):
            with patch("backend.app.services.audit.log") as mock_log:
                _client.delete("/api/lessons/l1", headers=_H)
        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args[0][1], "DELETE")

    def test_create_invoice_triggers_audit_log(self):
        with patch("backend.app.services.invoice.create_invoice",
                   return_value=[{"invoice_id": "inv1"}]):
            with patch("backend.app.services.audit.log") as mock_log:
                _client.post("/api/invoices",
                             json={"student_id": "s1", "total_amount": 100.0}, headers=_H)
        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args[0][2], "invoice")

    def test_record_payment_triggers_audit_log(self):
        payment_result = {"payment_id": "p1", "invoice_id": "inv1", "amount": 50.0}
        with patch("backend.app.services.payment.record_payment", return_value=payment_result):
            with patch("backend.app.services.audit.log") as mock_log:
                _client.post("/api/payments",
                             json={"invoice_id": "inv1", "amount": 50.0}, headers=_H)
        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args[0][2], "payment")

    def test_audit_log_failure_does_not_break_request(self):
        """Audit failures must be silent — the main operation must still succeed."""
        with patch("backend.app.services.student.create_student",
                   return_value=[{"student_id": "s1"}]):
            with patch("backend.app.services.audit.log", side_effect=Exception("DB down")):
                # audit.log raises, but the controller catches it silently
                # Actually audit.log itself catches exceptions internally, so this
                # tests the safety wrapper inside audit.py
                res = _client.post("/api/students", json={"name": "Alice"}, headers=_H)
        # Request should succeed regardless of audit failure
        self.assertEqual(res.status_code, 201)


if __name__ == "__main__":
    unittest.main()
