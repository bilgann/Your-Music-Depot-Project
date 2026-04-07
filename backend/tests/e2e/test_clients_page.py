"""
E2E tests -- Flow 9: Clients Management Page

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_clients_page.py -v
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase

UNIQUE = str(int(time.time()))


class TestClientsPage(E2EBase):
    """Covers: page renders, search, pagination, add/edit/delete client, row click."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self._get("/clients")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-clients")))

    # ── Page structure ────────────────────────────────────────────────────────

    def test_page_renders_title(self):
        """Clients page must show 'Clients' as the title."""
        title = self._find(By.CSS_SELECTOR, ".page-navbar.page-clients h1")
        self.assertEqual(title.text.strip(), "Clients")

    def test_page_has_search_input(self):
        """Page must have a search input."""
        search = self._find(By.CSS_SELECTOR, ".table-search-input")
        self.assertTrue(search.is_displayed())

    def test_page_has_add_button(self):
        """Page must show an '+ Add Client' button."""
        btn = self._find(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self.assertIn("Add Client", btn.text)

    def test_table_renders_with_columns(self):
        """Data table must have Name, Email, Phone, Credits columns."""
        headers = self.driver.find_elements(By.CSS_SELECTOR, ".data-table thead th")
        texts = [h.text.strip() for h in headers]
        for expected in ["Name", "Email", "Phone", "Credits"]:
            self.assertIn(expected, texts)

    def test_pagination_present(self):
        """Pagination controls must be visible."""
        pagination = self._find(By.CSS_SELECTOR, ".pagination")
        self.assertTrue(pagination.is_displayed())

    # ── Search ────────────────────────────────────────────────────────────────

    def test_search_filters_table(self):
        """Typing in search should filter the table results."""
        rows_before = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows_before:
            self.skipTest("No client data -- cannot test search")
        search = self._find(By.CSS_SELECTOR, ".table-search-input")
        search.clear()
        search.send_keys("zzz_nonexistent_zzz")
        time.sleep(1)  # debounce + API call
        rows_after = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        # Either fewer rows or the empty state message
        empty = self.driver.find_elements(By.CSS_SELECTOR, ".table-empty")
        self.assertTrue(len(rows_after) < len(rows_before) or len(empty) > 0)

    # ── Add modal ─────────────────────────────────────────────────────────────

    def test_add_modal_opens(self):
        """Clicking '+ Add Client' must open a modal."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self.assertTrue(self._find(By.CSS_SELECTOR, ".modal-overlay").is_displayed())

    def test_add_modal_title(self):
        """Add modal must be titled 'Add Client'."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        title = self._find(By.CSS_SELECTOR, ".modal-header h2")
        self.assertIn("Add Client", title.text)

    def test_add_modal_has_name_email_phone_fields(self):
        """Modal must contain Name, Email, and Phone fields."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        labels = [lbl.text for lbl in content.find_elements(By.TAG_NAME, "label")]
        for expected in ["Name", "Email", "Phone"]:
            self.assertTrue(any(expected in l for l in labels), f"Missing field: {expected}")

    def test_add_modal_cancel_closes(self):
        """Clicking Cancel in the modal must close it."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        self._click(By.CSS_SELECTOR, ".modal-footer .btn-secondary")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))

    # ── CRUD cycle ────────────────────────────────────────────────────────────

    def test_create_edit_delete_client(self):
        """Full CRUD: create a client, edit it, then delete it."""
        client_name = f"E2E Client {UNIQUE}"
        edited_name = f"E2E Edited {UNIQUE}"

        # CREATE
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        inputs = self.driver.find_elements(By.CSS_SELECTOR, ".modal-content input")
        inputs[0].send_keys(client_name)
        inputs[1].send_keys(f"e2e_{UNIQUE}@test.com")
        self._click(By.CSS_SELECTOR, ".modal-footer button[type='submit']")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))
        time.sleep(1)

        # Verify the new client appears in the table
        self._find(By.CSS_SELECTOR, ".table-search-input").clear()
        self._find(By.CSS_SELECTOR, ".table-search-input").send_keys(client_name)
        time.sleep(1)
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        self.assertGreaterEqual(len(rows), 1, "Created client not found in table")

        # EDIT -- click the edit icon on the first matching row
        edit_btn = self._find(By.CSS_SELECTOR, ".actions-cell .btn-icon")
        edit_btn.click()
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        name_input = self.driver.find_elements(By.CSS_SELECTOR, ".modal-content input")[0]
        name_input.clear()
        name_input.send_keys(edited_name)
        self._click(By.CSS_SELECTOR, ".modal-footer button[type='submit']")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))
        time.sleep(1)

        # DELETE -- search for the edited name and delete
        self._find(By.CSS_SELECTOR, ".table-search-input").clear()
        self._find(By.CSS_SELECTOR, ".table-search-input").send_keys(edited_name)
        time.sleep(1)
        del_btn = self._find(By.CSS_SELECTOR, ".actions-cell .btn-icon--danger")
        del_btn.click()
        self._dismiss_alert_if_present()
        time.sleep(1)

    # ── Row navigation ────────────────────────────────────────────────────────

    def test_row_click_navigates_to_detail(self):
        """Clicking a table row must navigate to the client detail page."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No client data -- cannot test row click")
        rows[0].click()
        self.wait.until(EC.url_contains("/clients/"))
        self.assertRegex(self.driver.current_url, r"/clients/[a-f0-9-]+")


if __name__ == "__main__":
    import unittest
    unittest.main()