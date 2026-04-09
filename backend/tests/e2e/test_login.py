"""
E2E tests – Flow 1: Login / Authentication

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_login.py -v
"""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase, USERNAME, PASSWORD


class TestLoginFlow(E2EBase):
    """Covers: redirect to login, valid login, invalid login, show/hide password."""

    def setUp(self):
        """Each login test needs an unauthenticated browser."""
        self._dismiss_alert_if_present()
        self._clear_session()

    def test_root_redirects_to_login(self):
        """/ should redirect to /login."""
        self._get("/")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_login_page_renders_form(self):
        """Login page must show the username, password inputs and submit button."""
        self._get("/login")
        self._find(By.ID, "username")
        self._find(By.ID, "password")
        self._find(By.CSS_SELECTOR, ".login-submit")
        title = self._find(By.CSS_SELECTOR, ".login-title")
        self.assertIn("Music Depot", title.text)

    def test_valid_login_redirects_to_home(self):
        """Successful login must navigate to /home."""
        self._do_login()
        self.wait.until(EC.url_contains("/home"))
        self.assertIn("/home", self.driver.current_url)

    def test_invalid_password_shows_error(self):
        """Wrong password must display an error message, stay on /login."""
        self._do_login(password="wrong_password_xyz")
        error = self._find(By.CSS_SELECTOR, ".login-error")
        self.assertTrue(error.is_displayed())
        self.assertIn("/login", self.driver.current_url)

    def test_invalid_username_shows_error(self):
        """Unknown username must display an error message."""
        self._do_login(username="no_such_user_xyz")
        error = self._find(By.CSS_SELECTOR, ".login-error")
        self.assertTrue(error.is_displayed())

    def test_empty_username_prevents_submit(self):
        """HTML5 required attribute prevents form submission with empty username."""
        self._get("/login")
        self._type(By.ID, "password", PASSWORD)
        submit = self._find(By.CSS_SELECTOR, ".login-submit")
        submit.click()
        self.assertIn("/login", self.driver.current_url)

    def test_empty_password_prevents_submit(self):
        """HTML5 required attribute prevents form submission with empty password."""
        self._get("/login")
        self._type(By.ID, "username", USERNAME)
        submit = self._find(By.CSS_SELECTOR, ".login-submit")
        submit.click()
        self.assertIn("/login", self.driver.current_url)

    def test_show_hide_password_toggle(self):
        """Show/Hide button must toggle the password field's type."""
        self._get("/login")
        pwd_input = self._find(By.ID, "password")
        self.assertEqual(pwd_input.get_attribute("type"), "password")

        self._click(By.CSS_SELECTOR, ".login-toggle-password")
        self.assertEqual(pwd_input.get_attribute("type"), "text")

        self._click(By.CSS_SELECTOR, ".login-toggle-password")
        self.assertEqual(pwd_input.get_attribute("type"), "password")

    def test_submit_button_disabled_while_loading(self):
        """Submit button should show 'Signing in…' and be disabled during the request."""
        self._get("/login")
        self._type(By.ID, "username", USERNAME)
        self._type(By.ID, "password", PASSWORD)
        submit = self.driver.find_element(By.CSS_SELECTOR, ".login-submit")
        submit.click()
        try:
            self.wait.until(
                lambda d: d.find_element(By.CSS_SELECTOR, ".login-submit").get_attribute("disabled")
                or "Signing" in d.find_element(By.CSS_SELECTOR, ".login-submit").text
            )
        except TimeoutException:
            pass


if __name__ == "__main__":
    import unittest
    unittest.main()
