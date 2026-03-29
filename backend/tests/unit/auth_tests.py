import unittest

from backend.app.application.singletons import Auth


class AuthTests(unittest.TestCase):

    def setUp(self):
        Auth._instance = None
        self.auth = Auth(secret_key="test-secret")

    def tearDown(self):
        Auth._instance = None

    # ── authenticate ──────────────────────────────────────────────────────

    def test_authenticate_success_returns_token(self):
        token = self.auth.authenticate("barnes", "password")
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

    def test_authenticate_wrong_password_returns_none(self):
        token = self.auth.authenticate("barnes", "wrong")
        self.assertIsNone(token)

    def test_authenticate_wrong_username_returns_none(self):
        token = self.auth.authenticate("unknown", "password")
        self.assertIsNone(token)

    def test_authenticate_empty_credentials_returns_none(self):
        token = self.auth.authenticate("", "")
        self.assertIsNone(token)

    # ── get_user ──────────────────────────────────────────────────────────

    def test_get_user_valid_token_returns_user(self):
        token = self.auth.authenticate("barnes", "password")
        user = self.auth.get_user(token)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "barnes")
        self.assertEqual(user.id, 0)

    def test_get_user_invalid_token_returns_none(self):
        user = self.auth.get_user("not.a.real.token")
        self.assertIsNone(user)

    def test_get_user_garbage_string_returns_none(self):
        user = self.auth.get_user("garbage")
        self.assertIsNone(user)

    # ── drop_token ────────────────────────────────────────────────────────

    def test_drop_token_blacklists_token(self):
        token = self.auth.authenticate("barnes", "password")
        self.auth.drop_token(token)
        user = self.auth.get_user(token)
        self.assertIsNone(user)

    def test_drop_token_returns_true(self):
        token = self.auth.authenticate("barnes", "password")
        result = self.auth.drop_token(token)
        self.assertTrue(result)

    def test_get_user_after_logout_returns_none(self):
        token = self.auth.authenticate("barnes", "password")
        self.auth.drop_token(token)
        self.assertIsNone(self.auth.get_user(token))

    # ── singleton ─────────────────────────────────────────────────────────

    def test_singleton_returns_same_instance(self):
        second = Auth()
        self.assertIs(self.auth, second)


if __name__ == "__main__":
    unittest.main()