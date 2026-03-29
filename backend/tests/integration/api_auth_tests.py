import unittest
from unittest.mock import MagicMock

from backend.app.application.singletons import Auth
from backend.app.application.singletons.database import DatabaseConnection


class ApiAuthTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Prevent DatabaseConnection from trying to reach Supabase.
        # Setting _instance to a MagicMock means the singleton check
        # short-circuits and _initialize is never called.
        DatabaseConnection._instance = MagicMock()

        Auth._instance = None
        from backend import build_app
        flask_app = build_app()
        flask_app.config["TESTING"] = True
        cls.client = flask_app.test_client()

    def setUp(self):
        # Fresh Auth singleton for each test so blacklist doesn't bleed across.
        Auth._instance = None
        Auth()

    def tearDown(self):
        Auth._instance = None

    # ── POST /user/login ──────────────────────────────────────────────────

    def test_login_valid_credentials_returns_200_and_token(self):
        res = self.client.post("/user/login?username=barnes&password=password")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["success"])
        self.assertIsNotNone(body["data"])

    def test_login_wrong_password_returns_401(self):
        res = self.client.post("/user/login?username=barnes&password=wrong")
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.get_json()["success"])

    def test_login_unknown_user_returns_401(self):
        res = self.client.post("/user/login?username=nobody&password=password")
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.get_json()["success"])

    def test_login_missing_params_returns_401(self):
        res = self.client.post("/user/login")
        self.assertEqual(res.status_code, 401)

    # ── DELETE /user/logout ───────────────────────────────────────────────

    def test_logout_valid_token_returns_200(self):
        token = self.client.post("/user/login?username=barnes&password=password").get_json()["data"]
        res = self.client.delete("/user/logout", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

    def test_logout_no_header_returns_401(self):
        res = self.client.delete("/user/logout")
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.get_json()["success"])

    def test_logout_malformed_header_returns_401(self):
        res = self.client.delete("/user/logout", headers={"Authorization": "Token abc"})
        self.assertEqual(res.status_code, 401)

    def test_logout_blacklists_token(self):
        token = self.client.post("/user/login?username=barnes&password=password").get_json()["data"]
        self.client.delete("/user/logout", headers={"Authorization": f"Bearer {token}"})
        # Token should now be blacklisted — get_user returns None
        user = Auth().get_user(token)
        self.assertIsNone(user)


if __name__ == "__main__":
    unittest.main()