"""
E2E tests – Flow 6: Add Lesson Modal

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_add_lesson_modal.py -v
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestAddLessonModal(E2EBase):
    """Covers: modal open/close, form fields, cancel without saving."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self.driver.find_elements(By.CSS_SELECTOR, ".sidebar-link")[1].click()
        self.wait.until(EC.url_contains("/schedule"))
        self._click(By.CSS_SELECTOR, ".new-button")

    def test_modal_opens_when_new_lesson_clicked(self):
        """Clicking '+ New Lesson' must open the schedule modal."""
        self.assertTrue(self._find(By.CSS_SELECTOR, ".modal-overlay").is_displayed())

    def test_modal_title_is_schedule_new_lesson(self):
        """Modal title must read 'Schedule New Lesson'."""
        title = self._find(By.XPATH, "//div[@class='modal-content']//h2")
        self.assertIn("Schedule New Lesson", title.text)

    def test_modal_has_instrument_field(self):
        """Modal must contain an Instrument input."""
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        label = content.find_element(By.XPATH, ".//label[contains(text(),'Instrument')]")
        self.assertTrue(label.is_displayed())

    def test_modal_has_date_field(self):
        """Modal must contain a Date input of type 'date'."""
        date_input = self._find(By.CSS_SELECTOR, ".modal-content input[type='date']")
        self.assertTrue(date_input.is_displayed())

    def test_modal_has_start_time_field(self):
        """Modal must contain a Start Time input of type 'datetime-local'."""
        dt_inputs = self.driver.find_elements(
            By.CSS_SELECTOR, ".modal-content input[type='datetime-local']"
        )
        self.assertGreaterEqual(len(dt_inputs), 1)

    def test_modal_has_end_time_field(self):
        """Modal must contain both Start Time and End Time inputs."""
        dt_inputs = self.driver.find_elements(
            By.CSS_SELECTOR, ".modal-content input[type='datetime-local']"
        )
        self.assertGreaterEqual(len(dt_inputs), 2)

    def test_modal_has_save_button(self):
        """Modal must have a Save (submit) button."""
        btn = self._find(By.CSS_SELECTOR, ".modal-content button[type='submit']")
        self.assertTrue(btn.is_displayed())

    def test_modal_has_cancel_button(self):
        """Modal must have a Cancel button."""
        cancel = self._find(By.XPATH, "//div[@class='modal-buttons']//button[@type='button']")
        self.assertTrue(cancel.is_displayed())

    def test_cancel_button_closes_modal(self):
        """Clicking Cancel must dismiss the modal."""
        cancel = self._find(By.XPATH, "//div[@class='modal-buttons']//button[@type='button']")
        cancel.click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, ".modal-overlay")), 0)

    def test_clicking_overlay_closes_modal(self):
        """Clicking the overlay backdrop must close the modal."""
        overlay = self._find(By.CSS_SELECTOR, ".modal-overlay")
        webdriver.ActionChains(self.driver).move_to_element_with_offset(overlay, 5, 5).click().perform()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))

    def test_submit_with_empty_instrument_shows_validation(self):
        """Submitting without Instrument must trigger HTML5 validation (modal stays open)."""
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        content.find_element(By.CSS_SELECTOR, "input[type='date']").send_keys("2026-06-01")
        dt_inputs = content.find_elements(By.CSS_SELECTOR, "input[type='datetime-local']")
        dt_inputs[0].send_keys("2026-06-01T10:00")
        dt_inputs[1].send_keys("2026-06-01T11:00")
        content.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.assertGreater(len(self.driver.find_elements(By.CSS_SELECTOR, ".modal-overlay")), 0)


if __name__ == "__main__":
    import unittest
    unittest.main()
