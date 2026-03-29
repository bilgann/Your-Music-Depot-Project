"""
E2E tests – Flow 7: Edit Mode (lesson edit / delete buttons)

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_edit_mode.py -v

Note: tests that interact with per-lesson buttons require at least one lesson
to be present in the current week. They are skipped if no lessons exist.
"""

import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestEditModeButtons(E2EBase):
    """Covers: edit-mode toggle reveals per-lesson edit and delete buttons."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self.driver.find_elements(By.CSS_SELECTOR, ".sidebar-link")[1].click()
        self.wait.until(EC.url_contains("/schedule"))
        time.sleep(1)  # allow calendar to load lessons

    def _enter_edit_mode(self):
        self._click(By.CSS_SELECTOR, ".edit-cal-btn")

    def test_edit_mode_hides_new_lesson_button(self):
        """In edit mode the '+ New Lesson' button should still be present."""
        self._enter_edit_mode()
        self.assertTrue(self._find(By.CSS_SELECTOR, ".new-button").is_displayed())

    def test_edit_mode_shows_event_edit_buttons_if_lessons_exist(self):
        """If lessons are displayed, edit mode must reveal the ✎ edit button on each."""
        self._enter_edit_mode()
        edit_btns = self.driver.find_elements(By.CSS_SELECTOR, ".event-edit-btn")
        if not edit_btns:
            self.skipTest("No lessons in current week — cannot test edit buttons")
        for btn in edit_btns:
            self.assertTrue(btn.is_displayed())

    def test_edit_mode_shows_event_delete_buttons_if_lessons_exist(self):
        """If lessons are displayed, edit mode must reveal the ✕ delete button on each."""
        self._enter_edit_mode()
        del_btns = self.driver.find_elements(By.CSS_SELECTOR, ".event-delete-btn")
        if not del_btns:
            self.skipTest("No lessons in current week — cannot test delete buttons")
        for btn in del_btns:
            self.assertTrue(btn.is_displayed())

    def test_clicking_edit_button_opens_modal_with_existing_data(self):
        """Clicking ✎ on a lesson must open the modal pre-filled with 'Edit Lesson'."""
        self._enter_edit_mode()
        edit_btns = self.driver.find_elements(By.CSS_SELECTOR, ".event-edit-btn")
        if not edit_btns:
            self.skipTest("No lessons in current week — cannot test edit modal")
        edit_btns[0].click()
        modal_title = self._find(By.XPATH, "//div[@class='modal-content']//h2")
        self.assertIn("Edit Lesson", modal_title.text)

    def test_clicking_delete_button_prompts_confirmation(self):
        """Clicking ✕ on a lesson must trigger a browser confirm dialog."""
        self._enter_edit_mode()
        del_btns = self.driver.find_elements(By.CSS_SELECTOR, ".event-delete-btn")
        if not del_btns:
            self.skipTest("No lessons in current week — cannot test delete confirmation")
        del_btns[0].click()
        try:
            alert = self.wait.until(EC.alert_is_present())
            self.assertIsNotNone(alert)
            alert.dismiss()
        except TimeoutException:
            self.fail("Expected a confirmation dialog after clicking delete")

    def test_save_edit_mode_closes_action_buttons(self):
        """Clicking ✓ (Save) in the calendar header must exit edit mode."""
        self._enter_edit_mode()
        self._click(By.CSS_SELECTOR, ".top-save-btn")
        self.assertTrue(self._find(By.CSS_SELECTOR, ".edit-cal-btn").is_displayed())


if __name__ == "__main__":
    import unittest
    unittest.main()
