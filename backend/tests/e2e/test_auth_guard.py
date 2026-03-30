"""
E2E tests -- Flow 17: Auth Guards on Protected Routes

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_auth_guard.py -v

Verifies that all protected pages redirect to /login when no token is present.
"""

from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestAuthGuards(E2EBase):
    """Covers: every protected route redirects to /login without authentication."""

    PROTECTED_ROUTES = [
        "/home",
        "/clients",
        "/students",
        "/instructors",
        "/rooms",
        "/payments",
        "/settings",
    ]

    def test_home_requires_auth(self):
        self._get("/home")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_clients_requires_auth(self):
        self._get("/clients")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_students_requires_auth(self):
        self._get("/students")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_instructors_requires_auth(self):
        self._get("/instructors")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_rooms_requires_auth(self):
        self._get("/rooms")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_payments_requires_auth(self):
        self._get("/payments")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_settings_requires_auth(self):
        self._get("/settings")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_direct_url_with_token_works(self):
        """After login, direct URL navigation should work for all protected routes."""
        self._login_and_wait_home()
        for route in self.PROTECTED_ROUTES:
            self._get(route)
            self.wait.until(EC.url_contains(route))
            self.assertIn(route, self.driver.current_url,
                          f"Direct URL navigation to {route} failed")


if __name__ == "__main__":
    import unittest
    unittest.main()
