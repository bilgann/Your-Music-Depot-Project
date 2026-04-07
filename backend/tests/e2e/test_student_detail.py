"""
E2E tests -- Flow 12: Student Detail Page

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_student_detail.py -v

Requires at least one student to exist in the database.
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestStudentDetailPage(E2EBase):
    """Covers: info card, Lessons and Invoices tabs, breadcrumb navigation."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self._get("/students")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-students")))
        time.sleep(1)
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No student data -- cannot test detail page")
        rows[0].click()
        self.wait.until(EC.url_contains("/students/"))

    # ── Page structure ────────────────────────────────────────────────────────

    def test_detail_page_renders(self):
        breadcrumb = self._find(By.CSS_SELECTOR, ".page-breadcrumb")
        self.assertTrue(breadcrumb.is_displayed())

    def test_breadcrumb_shows_students_link(self):
        link = self._find(By.CSS_SELECTOR, ".breadcrumb-link")
        self.assertEqual(link.text.strip(), "Students")

    def test_breadcrumb_navigates_back(self):
        self._click(By.CSS_SELECTOR, ".breadcrumb-link")
        self.wait.until(EC.url_contains("/students"))
        self.assertNotRegex(self.driver.current_url, r"/students/[a-f0-9-]+")

    # ── Tabs ──────────────────────────────────────────────────────────────────

    def test_tabs_visible(self):
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".client-tab")
        tab_labels = [t.text.strip() for t in tabs]
        for expected in ["Lessons", "Invoices"]:
            self.assertIn(expected, tab_labels)

    def test_lessons_tab_active_by_default(self):
        active = self._find(By.CSS_SELECTOR, ".client-tab.active")
        self.assertIn("Lessons", active.text)

    def test_switch_to_invoices_tab(self):
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".client-tab")
        for tab in tabs:
            if "Invoices" in tab.text:
                tab.click()
                break
        time.sleep(0.5)
        active = self._find(By.CSS_SELECTOR, ".client-tab.active")
        self.assertIn("Invoices", active.text)


if __name__ == "__main__":
    import unittest
    unittest.main()
