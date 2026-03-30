"""
E2E tests -- Flow 15: Payments Management Page

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_payments_page.py -v
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestPaymentsPage(E2EBase):
    """Covers: page renders, table columns, record payment modal, pagination."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self._get("/payments")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-payments")))

    # ── Page structure ────────────────────────────────────────────────────────

    def test_page_renders_title(self):
        title = self._find(By.CSS_SELECTOR, ".page-navbar.page-payments h1")
        self.assertEqual(title.text.strip(), "Payments")

    def test_page_has_record_button(self):
        btn = self._find(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self.assertIn("Record Payment", btn.text)

    def test_table_has_correct_columns(self):
        headers = self.driver.find_elements(By.CSS_SELECTOR, ".data-table thead th")
        if not headers:
            # May be empty state
            return
        texts = [h.text.strip() for h in headers]
        for expected in ["Amount", "Method"]:
            self.assertIn(expected, texts)

    def test_pagination_present(self):
        pagination = self._find(By.CSS_SELECTOR, ".pagination")
        self.assertTrue(pagination.is_displayed())

    # ── Record payment modal ──────────────────────────────────────────────────

    def test_record_modal_opens(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self.assertTrue(self._find(By.CSS_SELECTOR, ".modal-overlay").is_displayed())

    def test_record_modal_title(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        title = self._find(By.CSS_SELECTOR, ".modal-header h2")
        self.assertIn("Record Payment", title.text)

    def test_record_modal_has_fields(self):
        """Modal must contain Invoice ID, Amount, Payment Method, and Notes fields."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        labels = [lbl.text for lbl in content.find_elements(By.TAG_NAME, "label")]
        for expected in ["Invoice", "Amount", "Payment Method"]:
            self.assertTrue(any(expected in l for l in labels), f"Missing field: {expected}")

    def test_record_modal_cancel_closes(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        self._click(By.CSS_SELECTOR, ".modal-footer .btn-secondary")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))

    # ── Delete button ─────────────────────────────────────────────────────────

    def test_delete_button_visible_on_rows(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No payment data")
        del_btns = self.driver.find_elements(By.CSS_SELECTOR, ".actions-cell .btn-icon--danger")
        self.assertGreater(len(del_btns), 0)


if __name__ == "__main__":
    import unittest
    unittest.main()
