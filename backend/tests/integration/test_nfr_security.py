"""
Integration tests covering:
  NFR-08 — Access Control: JWT auth; admin-only financial data
  NFR-09 — Data Privacy: personal data requires authentication
  NFR-10 — Session Management: blacklisting, expiry, inactivity timeout
"""
import unittest
from unittest.mock import MagicMock, patch

import jwt

from backend.app.application.singletons import Auth
from backend.app.application.singletons.database import DatabaseConnection

_SECRET = "supersecretkey"


def _build():
    DatabaseConnection._instance = MagicMock()
    Auth._instance = None
    from backend import build_app
    app = build_app()
    app.config["TESTING"] = True
    return app.test_client()


_client = _build()


def _login():
    Auth._instance = None
    Auth()
    res = _client.post("/user/login?username=barnes&password=password")
    return res.get_json()["data"]


# ── NFR-08: Authentication ────────────────────────────────────────────────────

class TestNFRAuthentication(unittest.TestCase):
    """NFR-08: Users must authenticate via username/password to receive a JWT."""

    def setUp(self):
        Auth._instance = None
        Auth()

    def tearDown(self):
        Auth._instance = None

    def test_valid_credentials_return_200_and_token(self):
        res = _client.post("/user/login?username=barnes&password=password")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["success"])
        self.assertIsNotNone(body["data"])

    def test_returned_token_is_a_jwt(self):
        token = _login()
        self.assertEqual(len(token.split(".")), 3)

    def test_jwt_payload_includes_username_and_role(self):
        """NFR-08: JWT identifies the user and their role."""
        token = _login()
        payload = jwt.decode(token, options={"verify_signature": False})
        self.assertIn("username", payload)
        self.assertEqual(payload["username"], "barnes")
        self.assertIn("role", payload)

    def test_wrong_password_returns_401(self):
        res = _client.post("/user/login?username=barnes&password=wrong")
        self.assertEqual(res.status_code, 401)

    def test_unknown_user_returns_401(self):
        res = _client.post("/user/login?username=nobody&password=password")
        self.assertEqual(res.status_code, 401)

    def test_no_credentials_returns_401(self):
        res = _client.post("/user/login")
        self.assertEqual(res.status_code, 401)

    def test_response_does_not_expose_password(self):
        """NFR-09: Login response must not echo back the password."""
        res = _client.post("/user/login?username=barnes&password=password")
        body = res.get_json()
        self.assertNotIn("password", str(body.get("data", "")))


# ── NFR-08/09: Protected resource endpoints ───────────────────────────────────

class TestNFRProtectedRoutes(unittest.TestCase):
    """
    NFR-08, NFR-09: Resource endpoints require a valid JWT;
    financial endpoints require admin role.
    """

    def setUp(self):
        Auth._instance = None
        Auth()

    def tearDown(self):
        Auth._instance = None

    def test_student_list_requires_auth(self):
        """NFR-09: /api/students without token → 401."""
        with patch("backend.app.services.student.get_all_students", return_value=[]):
            res = _client.get("/api/students")
        self.assertEqual(res.status_code, 401)

    def test_instructor_list_requires_auth(self):
        """NFR-09: /api/instructors without token → 401."""
        with patch("backend.app.services.instructor.get_all_instructors", return_value=[]):
            res = _client.get("/api/instructors")
        self.assertEqual(res.status_code, 401)

    def test_lesson_list_requires_auth(self):
        with patch("backend.app.services.lesson.get_all_lessons", return_value=[]):
            res = _client.get("/api/lessons")
        self.assertEqual(res.status_code, 401)

    def test_invoices_require_auth(self):
        """NFR-08: Financial endpoint blocked without token."""
        with patch("backend.app.services.invoice.get_all_invoices", return_value=[]):
            res = _client.get("/api/invoices")
        self.assertEqual(res.status_code, 401)

    def test_payments_require_auth(self):
        """NFR-08: Payment endpoint blocked without token."""
        with patch("backend.app.services.payment.get_all_payments", return_value=[]):
            res = _client.get("/api/payments")
        self.assertEqual(res.status_code, 401)

    def test_invoices_blocked_for_instructor_role(self):
        """NFR-08: Instructor-role JWT must be denied access to invoice data."""
        # Craft a valid JWT with role=instructor
        instructor_token = jwt.encode(
            {"user_id": "i1", "username": "test_instructor", "role": "instructor"},
            _SECRET, algorithm="HS256",
        )
        with patch("backend.app.services.invoice.get_all_invoices", return_value=[]):
            res = _client.get("/api/invoices",
                              headers={"Authorization": f"Bearer {instructor_token}"})
        self.assertEqual(res.status_code, 403)

    def test_payments_blocked_for_instructor_role(self):
        """NFR-08: Instructor-role JWT must be denied access to payment data."""
        instructor_token = jwt.encode(
            {"user_id": "i1", "username": "test_instructor", "role": "instructor"},
            _SECRET, algorithm="HS256",
        )
        with patch("backend.app.services.payment.get_all_payments", return_value=[]):
            res = _client.get("/api/payments",
                              headers={"Authorization": f"Bearer {instructor_token}"})
        self.assertEqual(res.status_code, 403)

    def test_admin_can_access_invoices(self):
        """NFR-08: Admin-role JWT is permitted to see invoice data."""
        token = _login()
        with patch("backend.app.services.invoice.get_all_invoices", return_value=[]):
            res = _client.get("/api/invoices", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)


# ── NFR-10: Session Management ────────────────────────────────────────────────

class TestNFRSessionManagement(unittest.TestCase):
    """NFR-10: Tokens are blacklisted on logout; expired/tampered tokens rejected."""

    def setUp(self):
        Auth._instance = None
        Auth()

    def tearDown(self):
        Auth._instance = None

    def test_logout_returns_200(self):
        token = _login()
        res = _client.delete("/user/logout", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)

    def test_logout_blacklists_token(self):
        """NFR-10: After logout the same token is no longer valid."""
        token = _login()
        _client.delete("/user/logout", headers={"Authorization": f"Bearer {token}"})
        self.assertIsNone(Auth().get_user(token))

    def test_reusing_blacklisted_token_returns_401(self):
        """NFR-10: Blacklisted token cannot be reused for logout."""
        token = _login()
        _client.delete("/user/logout", headers={"Authorization": f"Bearer {token}"})
        res = _client.delete("/user/logout", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 401)

    def test_logout_without_header_returns_401(self):
        res = _client.delete("/user/logout")
        self.assertEqual(res.status_code, 401)

    def test_logout_malformed_header_returns_401(self):
        res = _client.delete("/user/logout", headers={"Authorization": "Basic abc"})
        self.assertEqual(res.status_code, 401)

    def test_expired_token_is_rejected(self):
        """NFR-10: Tokens with exp in the past are rejected by get_user."""
        expired = jwt.encode(
            {"user_id": "u1", "username": "barnes", "role": "admin", "exp": 1},
            _SECRET, algorithm="HS256",
        )
        self.assertIsNone(Auth().get_user(expired))

    def test_tampered_token_is_rejected(self):
        """NFR-10: Modified signature causes get_user to return None."""
        token = _login()
        self.assertIsNone(Auth().get_user(token[:-5] + "XXXXX"))

    def test_token_expiry_claim_is_present(self):
        """NFR-10: Token contains exp claim for time-based expiry."""
        token = _login()
        payload = jwt.decode(token, options={"verify_signature": False})
        self.assertIn("exp", payload)

    def test_inactive_token_is_rejected_after_30_minutes(self):
        """NFR-10: Token becomes invalid after 30 minutes of inactivity."""
        import datetime
        token = _login()
        auth = Auth()
        # Simulate the token having been last used 31 minutes ago
        auth._last_active[token] = (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=31)
        )
        self.assertIsNone(auth.get_user(token))

    def test_active_token_not_expired_by_inactivity(self):
        """NFR-10: Token still valid within the 30-minute window."""
        token = _login()
        auth = Auth()
        user = auth.get_user(token)
        self.assertIsNotNone(user)

    @unittest.skip("NFR-10 server-side inactivity tracking is in-memory only; "
                   "verify via test_inactive_token_is_rejected_after_30_minutes instead")
    def test_session_times_out_via_api_call(self):
        """Full round-trip inactivity test requires time manipulation beyond unit scope."""
        pass


if __name__ == "__main__":
    unittest.main()
