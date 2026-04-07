"""
E2E tests -- Flow 16: Settings Page

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_settings_page.py -v
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase, USERNAME


class TestSettingsPage(E2EBase):
    """Covers: page renders, displays username, role, and user ID from JWT."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self._get("/settings")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-settings")))

    def test_page_renders_title(self):
        title = self._find(By.CSS_SELECTOR, ".page-navbar.page-settings h1")
        self.assertEqual(title.text.strip(), "Settings")

    def test_settings_card_present(self):
        card = self._find(By.CSS_SELECTOR, ".settings-card")
        self.assertTrue(card.is_displayed())

    def test_shows_username_label(self):
        labels = self.driver.find_elements(By.CSS_SELECTOR, ".settings-label")
        texts = [l.text.strip() for l in labels]
        self.assertIn("Username", texts)

    def test_shows_role_label(self):
        labels = self.driver.find_elements(By.CSS_SELECTOR, ".settings-label")
        texts = [l.text.strip() for l in labels]
        self.assertIn("Role", texts)

    def test_shows_user_id_label(self):
        labels = self.driver.find_elements(By.CSS_SELECTOR, ".settings-label")
        texts = [l.text.strip() for l in labels]
        self.assertIn("User ID", texts)

    def test_username_value_matches_login(self):
        """The displayed username must match the login username."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".settings-row")
        for row in rows:
            label = row.find_element(By.CSS_SELECTOR, ".settings-label").text.strip()
            if label == "Username":
                value = row.find_element(By.CSS_SELECTOR, ".settings-value").text.strip()
                self.assertEqual(value, USERNAME)
                return
        self.fail("Username row not found")

    def test_role_value_is_admin(self):
        """The default test user should have the admin role."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".settings-row")
        for row in rows:
            label = row.find_element(By.CSS_SELECTOR, ".settings-label").text.strip()
            if label == "Role":
                value = row.find_element(By.CSS_SELECTOR, ".settings-value").text.strip()
                self.assertEqual(value, "admin")
                return
        self.fail("Role row not found")

    def test_user_id_is_non_empty(self):
        """The User ID value must be a non-empty string."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".settings-row")
        for row in rows:
            label = row.find_element(By.CSS_SELECTOR, ".settings-label").text.strip()
            if label == "User ID":
                value = row.find_element(By.CSS_SELECTOR, ".settings-value").text.strip()
                self.assertGreater(len(value), 0)
                self.assertNotEqual(value, "Unknown")
                return
        self.fail("User ID row not found")


if __name__ == "__main__":
    import unittest
    unittest.main()
