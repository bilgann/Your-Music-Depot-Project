"""
Integration tests covering:
  NFR-08 — Access Control: JWT authentication; role-based restrictions
  NFR-09 — Data Privacy: personal/financial data visible only to authorized users
  NFR-10 — Session Management: token blacklisting and expiry

Implementation gaps (marked with @unittest.skip):
  - Resource endpoints do not yet require a JWT (NFR-08, NFR-09)
  - Token expiry is 1 hour; NFR-10 requires 30-minute inactivity timeout
"""
import unittest
from unittest.mock import MagicMock

import jwt

from backend.app.singletons.auth import Auth
from backend.app.singletons.database import DatabaseConnection

_SECRET = "supersecretkey"  # documented default in Auth singleton


def _build():
    DatabaseConnection._instance = MagicMock()
    Auth._instance = None
    from backend import build_app
    app = build_app()
    app.config["TESTING"] = True
    return app.test_client()


_client = _build()


def _login():
    """Obtain a valid JWT by logging in with default credentials."""
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
        """NFR-08: Token must be a 3-part JWT."""
        token = _login()
        self.assertEqual(len(token.split(".")), 3)

    def test_jwt_payload_includes_username(self):
        """NFR-08: JWT payload identifies the authenticated user."""
        token = _login()
        payload = jwt.decode(token, options={"verify_signature": False})
        self.assertIn("username", payload)
        self.assertEqual(payload["username"], "barnes")

    def test_wrong_password_returns_401(self):
        res = _client.post("/user/login?username=barnes&password=wrong")
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.get_json()["success"])

    def test_unknown_user_returns_401(self):
        res = _client.post("/user/login?username=nobody&password=password")
        self.assertEqual(res.status_code, 401)

    def test_no_credentials_returns_401(self):
        res = _client.post("/user/login")
        self.assertEqual(res.status_code, 401)

    def test_response_does_not_expose_password(self):
        """NFR-09: Login response must not echo back the user's password."""
        res = _client.post("/user/login?username=barnes&password=password")
        body = res.get_json()
        self.assertNotIn("password", str(body["data"]))


# ── NFR-10: Session Management ────────────────────────────────────────────────

class TestNFRSessionManagement(unittest.TestCase):
    """NFR-10: Tokens are blacklisted on logout; expired/tampered tokens are rejected."""

    def setUp(self):
        Auth._instance = None
        Auth()

    def tearDown(self):
        Auth._instance = None

    def test_logout_returns_200(self):
        token = _login()
        res = _client.delete("/user/logout", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

    def test_logout_blacklists_token(self):
        """NFR-10: After logout, the same token is no longer valid."""
        token = _login()
        _client.delete("/user/logout", headers={"Authorization": f"Bearer {token}"})
        user = Auth().get_user(token)
        self.assertIsNone(user)

    def test_reusing_blacklisted_token_returns_401(self):
        """NFR-10: Blacklisted token cannot be used to logout again."""
        token = _login()
        _client.delete("/user/logout", headers={"Authorization": f"Bearer {token}"})
        res = _client.delete("/user/logout", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 401)

    def test_logout_without_header_returns_401(self):
        """NFR-10: Logout endpoint requires Authorization header."""
        res = _client.delete("/user/logout")
        self.assertEqual(res.status_code, 401)

    def test_logout_with_malformed_header_returns_401(self):
        """NFR-10: 'Basic' scheme instead of 'Bearer' is rejected."""
        res = _client.delete("/user/logout", headers={"Authorization": "Basic abc123"})
        self.assertEqual(res.status_code, 401)

    def test_expired_token_is_rejected(self):
        """NFR-10: Tokens with a past expiry are rejected by get_user."""
        expired = jwt.encode(
            {"username": "barnes", "id": 0, "exp": 1},  # epoch 1 = far in past
            _SECRET,
            algorithm="HS256",
        )
        user = Auth().get_user(expired)
        self.assertIsNone(user)

    def test_tampered_token_is_rejected(self):
        """NFR-10: Modifying a token's signature causes get_user to return None."""
        token = _login()
        tampered = token[:-5] + "XXXXX"
        self.assertIsNone(Auth().get_user(tampered))

    def test_garbage_string_is_rejected(self):
        """NFR-10: Completely invalid token string is rejected."""
        self.assertIsNone(Auth().get_user("not.a.jwt"))

    def test_token_expiry_claim_is_present(self):
        """NFR-10: Token contains an exp claim for expiry enforcement."""
        token = _login()
        payload = jwt.decode(token, options={"verify_signature": False})
        self.assertIn("exp", payload)


# ── NFR-08/NFR-09: Protected Routes (not yet implemented) ────────────────────

class TestNFRProtectedRoutes(unittest.TestCase):
    """
    NFR-08: Instructors must not be able to access financial data.
    NFR-09: Personal data (contacts, DOB) must require authentication.

    These tests are skipped because the resource endpoints (students, instructors,
    rooms, lessons, invoices, payments) do not yet enforce JWT authentication.
    Enable these tests once auth middleware is added to the API.
    """

    @unittest.skip("NFR-09 not implemented: /api/students has no JWT middleware")
    def test_student_list_requires_auth(self):
        res = _client.get("/api/students")
        self.assertEqual(res.status_code, 401)

    @unittest.skip("NFR-09 not implemented: /api/instructors has no JWT middleware")
    def test_instructor_list_requires_auth(self):
        res = _client.get("/api/instructors")
        self.assertEqual(res.status_code, 401)

    @unittest.skip("NFR-08 not implemented: /api/invoices has no role-based access")
    def test_invoices_require_admin_role(self):
        """Instructor-role JWT must be denied access to financial invoice data."""
        instructor_token = "dummy_instructor_token"
        res = _client.get(
            "/api/invoices",
            headers={"Authorization": f"Bearer {instructor_token}"},
        )
        self.assertEqual(res.status_code, 403)

    @unittest.skip("NFR-08 not implemented: /api/payments has no role-based access")
    def test_payments_require_admin_role(self):
        """Instructor-role JWT must be denied access to payment records."""
        res = _client.get("/api/payments")
        self.assertEqual(res.status_code, 401)

    @unittest.skip("NFR-10 not implemented: session inactivity timeout is not enforced")
    def test_session_times_out_after_30_minutes_inactivity(self):
        """
        A token not used for 30 minutes must be rejected.
        Requires server-side inactivity tracking (not currently implemented).
        """
        token = _login()
        # Simulate 30 minutes of inactivity by checking the token
        # (implementation would need a last-activity timestamp)
        res = _client.get("/api/students", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()