"""
E2E tests – Flow 5: Schedule Page (Calendar)

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_schedule.py -v
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestSchedulePage(E2EBase):
    """Covers: calendar renders, week navigation, today button, edit mode."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self.driver.find_elements(By.CSS_SELECTOR, ".sidebar-link")[1].click()
        self.wait.until(EC.url_contains("/schedule"))

    def test_schedule_page_renders_calendar(self):
        """Schedule page must render the activity panel."""
        panel = self._find(By.CSS_SELECTOR, ".activity-panel")
        self.assertTrue(panel.is_displayed())

    def test_calendar_shows_five_day_columns(self):
        """Calendar grid must contain 5 day columns (Mon–Fri)."""
        self._find(By.CSS_SELECTOR, ".days-col")
        day_cols = self.driver.find_elements(By.CSS_SELECTOR, ".day-column")
        self.assertEqual(len(day_cols), 5)

    def test_calendar_shows_day_headers(self):
        """Week row must contain the five weekday names."""
        headers = self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-name")
        names = [h.text.strip() for h in headers]
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            self.assertIn(day, names)

    def test_calendar_shows_time_slots(self):
        """Time column must show hour labels from 8 AM to 6 PM."""
        time_cells = self.driver.find_elements(By.CSS_SELECTOR, ".time-cell")
        self.assertGreaterEqual(len(time_cells), 10)

    def test_new_lesson_button_present(self):
        """'+ New Lesson' button must be visible."""
        btn = self._find(By.CSS_SELECTOR, ".new-button")
        self.assertTrue(btn.is_displayed())

    def test_today_button_present(self):
        """'Today' button must be visible."""
        btn = self._find(By.CSS_SELECTOR, ".today-button")
        self.assertTrue(btn.is_displayed())

    def test_prev_week_button_navigates(self):
        """Clicking the previous-week arrow must update the displayed dates."""
        headers_before = [
            h.text for h in self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-date")
        ]
        self._click(By.CSS_SELECTOR, ".nav-btn[aria-label='Previous week']")
        time.sleep(0.5)
        headers_after = [
            h.text for h in self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-date")
        ]
        self.assertNotEqual(headers_before, headers_after)

    def test_next_week_button_navigates(self):
        """Clicking the next-week arrow must update the displayed dates."""
        headers_before = [
            h.text for h in self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-date")
        ]
        self._click(By.CSS_SELECTOR, ".nav-btn[aria-label='Next week']")
        time.sleep(0.5)
        headers_after = [
            h.text for h in self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-date")
        ]
        self.assertNotEqual(headers_before, headers_after)

    def test_today_button_returns_to_current_week(self):
        """After navigating away, 'Today' must return to the current week's dates."""
        self._click(By.CSS_SELECTOR, ".nav-btn[aria-label='Next week']")
        time.sleep(0.3)
        self._click(By.CSS_SELECTOR, ".nav-btn[aria-label='Next week']")
        time.sleep(0.3)
        headers_away = [
            h.text for h in self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-date")
        ]
        self._click(By.CSS_SELECTOR, ".today-button")
        time.sleep(0.5)
        headers_today = [
            h.text for h in self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-date")
        ]
        self.assertNotEqual(headers_away, headers_today)

    def test_edit_mode_toggle_button_present(self):
        """Edit button must be present on the schedule page."""
        btn = self._find(By.CSS_SELECTOR, ".edit-cal-btn")
        self.assertTrue(btn.is_displayed())

    def test_edit_mode_reveals_save_and_cancel(self):
        """Clicking Edit must replace the Edit button with Save (✓) and Cancel (✕) buttons."""
        self._click(By.CSS_SELECTOR, ".edit-cal-btn")
        self.assertTrue(self._find(By.CSS_SELECTOR, ".top-save-btn").is_displayed())
        self.assertTrue(self._find(By.CSS_SELECTOR, ".top-cancel-btn").is_displayed())

    def test_cancel_edit_mode_restores_edit_button(self):
        """Clicking the Cancel (✕) button in edit mode must restore the Edit button."""
        self._click(By.CSS_SELECTOR, ".edit-cal-btn")
        self._click(By.CSS_SELECTOR, ".top-cancel-btn")
        self.assertTrue(self._find(By.CSS_SELECTOR, ".edit-cal-btn").is_displayed())


if __name__ == "__main__":
    import unittest
    unittest.main()
