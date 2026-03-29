"""
E2E tests – Flow 2: Dashboard Home

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_dashboard.py -v
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestDashboardHome(E2EBase):
    """Covers: dashboard stats, quick-action buttons, auth guard."""

    def test_home_requires_authentication(self):
        """/home without a token must redirect to /login."""
        self._get("/home")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_home_renders_after_login(self):
        """After login, /home must display the dashboard title."""
        self._login_and_wait_home()
        title = self._find(By.CSS_SELECTOR, ".dashboard-title")
        self.assertEqual(title.text.strip(), "Dashboard")

    def test_home_shows_today_lessons_stat(self):
        """Dashboard must render the 'Today's Lessons' stat card."""
        self._login_and_wait_home()
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".stat-card")
        labels = [c.find_element(By.CSS_SELECTOR, ".stat-label").text for c in cards]
        self.assertIn("Today's Lessons", labels)

    def test_home_shows_next_lesson_stat(self):
        """Dashboard must render the 'Next Lesson' stat card."""
        self._login_and_wait_home()
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".stat-card")
        labels = [c.find_element(By.CSS_SELECTOR, ".stat-label").text for c in cards]
        self.assertIn("Next Lesson", labels)

    def test_add_lesson_button_navigates_to_schedule(self):
        """'+ Add Lesson' button must navigate to /schedule."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".action-btn--primary")
        self.wait.until(EC.url_contains("/schedule"))
        self.assertIn("/schedule", self.driver.current_url)

    def test_add_student_button_navigates_to_students(self):
        """'+ Add Student' button must navigate to /students."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".action-btn--secondary")
        self.wait.until(EC.url_contains("/students"))
        self.assertIn("/students", self.driver.current_url)

    def test_view_schedule_button_navigates_to_schedule(self):
        """'View Schedule' button must navigate to /schedule."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".action-btn--ghost")
        self.wait.until(EC.url_contains("/schedule"))
        self.assertIn("/schedule", self.driver.current_url)


if __name__ == "__main__":
    import unittest
    unittest.main()
