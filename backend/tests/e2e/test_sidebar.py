"""
E2E tests – Flow 3: Sidebar Navigation

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_sidebar.py -v
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


class TestSidebarNavigation(E2EBase):
    """Covers: all sidebar links, active state, logout button presence."""

    SIDEBAR_ROUTES = [
        ("Home",        "/home"),
        ("Schedule",    "/schedule"),
        ("Students",    "/students"),
        ("Instructors", "/instructors"),
        ("Rooms",       "/rooms"),
        ("Payments",    "/payments"),
        ("Settings",    "/settings"),
    ]

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()

    def _get_sidebar_link(self, label: str):
        links = self.driver.find_elements(By.CSS_SELECTOR, ".sidebar-link")
        for link in links:
            if link.text.strip() == label:
                return link
        self.fail(f"Sidebar link '{label}' not found")

    def test_sidebar_renders_all_links(self):
        """Sidebar must contain all 7 navigation items."""
        sidebar = self._find(By.CSS_SELECTOR, "aside.sidebar-container")
        links = sidebar.find_elements(By.CSS_SELECTOR, ".sidebar-link")
        link_texts = [l.text.strip() for l in links]
        for label, _ in self.SIDEBAR_ROUTES:
            self.assertIn(label, link_texts)

    def test_sidebar_home_link_navigates(self):
        self._click(By.CSS_SELECTOR, "aside.sidebar-container .sidebar-link")
        self.wait.until(EC.url_contains("/home"))
        self.assertIn("/home", self.driver.current_url)

    def test_sidebar_schedule_link_navigates(self):
        self._get_sidebar_link("Schedule").click()
        self.wait.until(EC.url_contains("/schedule"))
        self.assertIn("/schedule", self.driver.current_url)

    def test_sidebar_students_link_navigates(self):
        self._get_sidebar_link("Students").click()
        self.wait.until(EC.url_contains("/students"))
        self.assertIn("/students", self.driver.current_url)

    def test_sidebar_instructors_link_navigates(self):
        self._get_sidebar_link("Instructors").click()
        self.wait.until(EC.url_contains("/instructors"))
        self.assertIn("/instructors", self.driver.current_url)

    def test_sidebar_rooms_link_navigates(self):
        self._get_sidebar_link("Rooms").click()
        self.wait.until(EC.url_contains("/rooms"))
        self.assertIn("/rooms", self.driver.current_url)

    def test_sidebar_payments_link_navigates(self):
        self._get_sidebar_link("Payments").click()
        self.wait.until(EC.url_contains("/payments"))
        self.assertIn("/payments", self.driver.current_url)

    def test_sidebar_settings_link_navigates(self):
        self._get_sidebar_link("Settings").click()
        self.wait.until(EC.url_contains("/settings"))
        self.assertIn("/settings", self.driver.current_url)

    def test_active_link_has_active_class(self):
        """The sidebar link matching the current page should have the 'active' CSS class."""
        self._get_sidebar_link("Schedule").click()
        self.wait.until(EC.url_contains("/schedule"))
        active_link = self._find(By.CSS_SELECTOR, ".sidebar-link.active")
        self.assertIn("Schedule", active_link.text)

    def test_sidebar_logout_button_present(self):
        """Sidebar must contain a logout button."""
        btn = self._find(By.CSS_SELECTOR, ".sidebar-logout")
        self.assertTrue(btn.is_displayed())


if __name__ == "__main__":
    import unittest
    unittest.main()
