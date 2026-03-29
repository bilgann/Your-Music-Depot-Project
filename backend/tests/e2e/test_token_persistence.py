"""
E2E tests – Flow 8: Token Persistence (page refresh)

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_token_persistence.py -v
"""

from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestTokenPersistence(E2EBase):
    """Covers: session survives a page refresh; direct URL access after login."""

    def test_session_survives_page_refresh(self):
        """After login, refreshing the page must keep the user on /home."""
        self._login_and_wait_home()
        self.driver.refresh()
        self.wait.until(EC.url_contains("/home"))
        self.assertIn("/home", self.driver.current_url)

    def test_direct_url_access_to_schedule_after_login(self):
        """Navigating directly to /schedule after login must work without redirect."""
        self._login_and_wait_home()
        self._get("/schedule")
        self.wait.until(EC.url_contains("/schedule"))
        self.assertIn("/schedule", self.driver.current_url)

    def test_token_stored_in_local_storage_after_login(self):
        """After login, localStorage must contain a non-empty 'token' value."""
        self._login_and_wait_home()
        token = self.driver.execute_script("return localStorage.getItem('token');")
        self.assertIsNotNone(token)
        self.assertGreater(len(token), 10)

    def test_token_is_a_jwt_three_parts(self):
        """Token in localStorage must be a valid three-part JWT string."""
        self._login_and_wait_home()
        token = self.driver.execute_script("return localStorage.getItem('token');")
        parts = token.split(".")
        self.assertEqual(len(parts), 3, "Expected JWT with 3 dot-separated parts")


if __name__ == "__main__":
    import unittest
    unittest.main()
