"""
E2E tests -- Flow 10: Client Detail Page

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_client_detail.py -v

Requires at least one client to exist in the database.
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestClientDetailPage(E2EBase):
    """Covers: info card, tabs, action buttons, breadcrumb navigation."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self._get("/clients")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-clients")))
        time.sleep(1)
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No client data -- cannot test detail page")
        rows[0].click()
        self.wait.until(EC.url_contains("/clients/"))

    # ── Page structure ────────────────────────────────────────────────────────

    def test_detail_page_renders(self):
        """Client detail page must load with a breadcrumb."""
        breadcrumb = self._find(By.CSS_SELECTOR, ".page-breadcrumb")
        self.assertTrue(breadcrumb.is_displayed())

    def test_breadcrumb_shows_clients_link(self):
        """Breadcrumb must contain a 'Clients' link."""
        link = self._find(By.CSS_SELECTOR, ".breadcrumb-link")
        self.assertEqual(link.text.strip(), "Clients")

    def test_breadcrumb_navigates_back(self):
        """Clicking the 'Clients' breadcrumb must navigate back to /clients."""
        self._click(By.CSS_SELECTOR, ".breadcrumb-link")
        self.wait.until(EC.url_contains("/clients"))
        self.assertNotRegex(self.driver.current_url, r"/clients/[a-f0-9-]+")

    # ── Tabs ──────────────────────────────────────────────────────────────────

    def test_tabs_visible(self):
        """Students, Invoices, and Payments tabs must be visible."""
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".client-tab")
        tab_labels = [t.text.strip() for t in tabs]
        for expected in ["Students", "Invoices", "Payments"]:
            self.assertIn(expected, tab_labels)

    def test_students_tab_active_by_default(self):
        """The Students tab must be active by default."""
        active = self._find(By.CSS_SELECTOR, ".client-tab.active")
        self.assertIn("Students", active.text)

    def test_switch_to_invoices_tab(self):
        """Clicking the Invoices tab must switch the active tab."""
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".client-tab")
        for tab in tabs:
            if "Invoices" in tab.text:
                tab.click()
                break
        time.sleep(0.5)
        active = self._find(By.CSS_SELECTOR, ".client-tab.active")
        self.assertIn("Invoices", active.text)

    def test_switch_to_payments_tab(self):
        """Clicking the Payments tab must switch the active tab."""
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".client-tab")
        for tab in tabs:
            if "Payments" in tab.text:
                tab.click()
                break
        time.sleep(0.5)
        active = self._find(By.CSS_SELECTOR, ".client-tab.active")
        self.assertIn("Payments", active.text)

    # ── Action buttons ────────────────────────────────────────────────────────

    def test_add_payment_button_present(self):
        """The 'Add Payment' action button must be visible."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        texts = [b.text.strip() for b in btns]
        self.assertTrue(any("Payment" in t for t in texts))

    def test_add_student_button_present(self):
        """The 'Add Student' action button must be visible."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, ".page-navbar-actions .btn-secondary")
        texts = [b.text.strip() for b in btns]
        self.assertTrue(any("Student" in t for t in texts))

    def test_add_invoice_button_present(self):
        """The 'Add Invoice' action button must be visible."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, ".page-navbar-actions .btn-secondary")
        texts = [b.text.strip() for b in btns]
        self.assertTrue(any("Invoice" in t for t in texts))

    def test_add_payment_opens_modal(self):
        """Clicking 'Add Payment' must open a modal."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        for b in btns:
            if "Payment" in b.text:
                b.click()
                break
        self.assertTrue(self._find(By.CSS_SELECTOR, ".modal-overlay").is_displayed())


if __name__ == "__main__":
    import unittest
    unittest.main()