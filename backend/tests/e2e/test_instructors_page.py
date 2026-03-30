"""
E2E tests -- Flow 13: Instructors Management Page

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_instructors_page.py -v
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestInstructorsPage(E2EBase):
    """Covers: page renders, search, pagination, add/edit/delete instructor."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self._get("/instructors")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-instructor")))

    # ── Page structure ────────────────────────────────────────────────────────

    def test_page_renders_title(self):
        title = self._find(By.CSS_SELECTOR, ".page-navbar.page-instructor h1")
        self.assertEqual(title.text.strip(), "Instructors")

    def test_page_has_search_input(self):
        search = self._find(By.CSS_SELECTOR, ".table-search-input")
        self.assertTrue(search.is_displayed())

    def test_page_has_add_button(self):
        btn = self._find(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self.assertIn("Add Instructor", btn.text)

    def test_table_has_correct_columns(self):
        headers = self.driver.find_elements(By.CSS_SELECTOR, ".data-table thead th")
        texts = [h.text.strip() for h in headers]
        for expected in ["Name", "Email", "Phone"]:
            self.assertIn(expected, texts)

    def test_pagination_present(self):
        pagination = self._find(By.CSS_SELECTOR, ".pagination")
        self.assertTrue(pagination.is_displayed())

    # ── Search ────────────────────────────────────────────────────────────────

    def test_search_filters_table(self):
        rows_before = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows_before:
            self.skipTest("No instructor data")
        search = self._find(By.CSS_SELECTOR, ".table-search-input")
        search.clear()
        search.send_keys("zzz_nonexistent_zzz")
        time.sleep(1)
        rows_after = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        empty = self.driver.find_elements(By.CSS_SELECTOR, ".table-empty")
        self.assertTrue(len(rows_after) < len(rows_before) or len(empty) > 0)

    # ── Add modal ─────────────────────────────────────────────────────────────

    def test_add_modal_opens(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self.assertTrue(self._find(By.CSS_SELECTOR, ".modal-overlay").is_displayed())

    def test_add_modal_title(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        title = self._find(By.CSS_SELECTOR, ".modal-header h2")
        self.assertIn("Add Instructor", title.text)

    def test_add_modal_has_fields(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        labels = [lbl.text for lbl in content.find_elements(By.TAG_NAME, "label")]
        for expected in ["Name", "Email", "Phone"]:
            self.assertTrue(any(expected in l for l in labels), f"Missing field: {expected}")

    def test_add_modal_cancel_closes(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        self._click(By.CSS_SELECTOR, ".modal-footer .btn-secondary")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))

    # ── Table interactions ────────────────────────────────────────────────────

    def test_edit_button_visible_on_rows(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No instructor data")
        edit_btns = self.driver.find_elements(By.CSS_SELECTOR, ".actions-cell .btn-icon")
        self.assertGreater(len(edit_btns), 0)

    def test_delete_button_visible_on_rows(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No instructor data")
        del_btns = self.driver.find_elements(By.CSS_SELECTOR, ".actions-cell .btn-icon--danger")
        self.assertGreater(len(del_btns), 0)

    def test_edit_button_opens_edit_modal(self):
        edit_btns = self.driver.find_elements(By.CSS_SELECTOR, ".actions-cell .btn-icon")
        if not edit_btns:
            self.skipTest("No instructor data")
        edit_btns[0].click()
        title = self._find(By.CSS_SELECTOR, ".modal-header h2")
        self.assertIn("Edit Instructor", title.text)


if __name__ == "__main__":
    import unittest
    unittest.main()
