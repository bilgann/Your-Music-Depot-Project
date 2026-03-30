"""
E2E tests -- Flow 11: Students Management Page

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_students_page.py -v
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestStudentsPage(E2EBase):
    """Covers: page renders, search, pagination, add modal, row click to detail."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self._get("/students")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-students")))

    # ── Page structure ────────────────────────────────────────────────────────

    def test_page_renders_title(self):
        """Students page must show 'Students' as the title."""
        title = self._find(By.CSS_SELECTOR, ".page-navbar.page-students h1")
        self.assertEqual(title.text.strip(), "Students")

    def test_page_has_search_input(self):
        search = self._find(By.CSS_SELECTOR, ".table-search-input")
        self.assertTrue(search.is_displayed())

    def test_page_has_add_button(self):
        btn = self._find(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self.assertIn("Add Student", btn.text)

    def test_table_has_correct_columns(self):
        """Data table must have Name, Email, Phone, Client columns."""
        headers = self.driver.find_elements(By.CSS_SELECTOR, ".data-table thead th")
        texts = [h.text.strip() for h in headers]
        for expected in ["Name", "Email", "Phone", "Client"]:
            self.assertIn(expected, texts)

    def test_pagination_present(self):
        pagination = self._find(By.CSS_SELECTOR, ".pagination")
        self.assertTrue(pagination.is_displayed())

    # ── Search ────────────────────────────────────────────────────────────────

    def test_search_filters_table(self):
        rows_before = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows_before:
            self.skipTest("No student data")
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

    def test_add_modal_has_fields(self):
        """Modal must contain Name, Email, Phone, and Client fields."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        labels = [lbl.text for lbl in content.find_elements(By.TAG_NAME, "label")]
        for expected in ["Name", "Email", "Phone", "Client"]:
            self.assertTrue(any(expected in l for l in labels), f"Missing field: {expected}")

    def test_add_modal_cancel_closes(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        self._click(By.CSS_SELECTOR, ".modal-footer .btn-secondary")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))

    # ── Row navigation ────────────────────────────────────────────────────────

    def test_row_click_navigates_to_detail(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No student data")
        rows[0].click()
        self.wait.until(EC.url_contains("/students/"))
        self.assertRegex(self.driver.current_url, r"/students/[a-f0-9-]+")

    # ── Pagination navigation ─────────────────────────────────────────────────

    def test_pagination_next_page(self):
        """Clicking next page must change the pagination info text."""
        info = self._find(By.CSS_SELECTOR, ".pagination-info")
        if "1 of 1" in info.text:
            self.skipTest("Only one page of students")
        next_btn = self.driver.find_element(By.CSS_SELECTOR, ".pagination button[title='Next page']")
        if next_btn.get_attribute("disabled"):
            self.skipTest("Next page button disabled")
        next_btn.click()
        time.sleep(1)
        new_info = self._find(By.CSS_SELECTOR, ".pagination-info")
        self.assertIn("2", new_info.text)


if __name__ == "__main__":
    import unittest
    unittest.main()
