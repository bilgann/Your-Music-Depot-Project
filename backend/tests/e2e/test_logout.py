"""
E2E tests – Flow 4: Logout

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_logout.py -v
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestLogoutFlow(E2EBase):
    """Covers: logout button, redirect to login, token cleared."""

    def test_logout_redirects_to_login(self):
        """Clicking logout must redirect to /login."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".sidebar-logout")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_after_logout_protected_route_redirects(self):
        """After logout, navigating to /home must redirect back to /login."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".sidebar-logout")
        self.wait.until(EC.url_contains("/login"))
        self._get("/home")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_logout_clears_token_from_local_storage(self):
        """After logout, localStorage['token'] must be absent or null."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".sidebar-logout")
        self.wait.until(EC.url_contains("/login"))
        token = self.driver.execute_script("return localStorage.getItem('token');")
        self.assertIsNone(token)

    def test_can_login_again_after_logout(self):
        """User can complete a second login after logging out."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".sidebar-logout")
        self.wait.until(EC.url_contains("/login"))
        self._do_login()
        self.wait.until(EC.url_contains("/home"))
        self.assertIn("/home", self.driver.current_url)


if __name__ == "__main__":
    import unittest
    unittest.main()
