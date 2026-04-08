"""
E2E tests -- Flow 14: Rooms Management Page

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_rooms_page.py -v
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase

UNIQUE = str(int(time.time()))


class TestRoomsPage(E2EBase):
    """Covers: page renders, search, pagination, add/edit/delete room."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self._get("/rooms")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-rooms")))

    # ── Page structure ────────────────────────────────────────────────────────

    def test_page_renders_title(self):
        title = self._find(By.CSS_SELECTOR, ".page-navbar.page-rooms h1")
        self.assertEqual(title.text.strip(), "Rooms")

    def test_page_has_search_input(self):
        search = self._find(By.CSS_SELECTOR, ".table-search-input")
        self.assertTrue(search.is_displayed())

    def test_page_has_add_button(self):
        btn = self._find(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self.assertIn("Add Room", btn.text)

    def test_table_has_correct_columns(self):
        headers = self.driver.find_elements(By.CSS_SELECTOR, ".data-table thead th")
        texts = [h.text.strip() for h in headers]
        for expected in ["Name", "Capacity"]:
            self.assertIn(expected, texts)

    def test_pagination_present(self):
        pagination = self._find(By.CSS_SELECTOR, ".pagination")
        self.assertTrue(pagination.is_displayed())

    # ── Add modal ─────────────────────────────────────────────────────────────

    def test_add_modal_opens(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self.assertTrue(self._find(By.CSS_SELECTOR, ".modal-overlay").is_displayed())

    def test_add_modal_title(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        title = self._find(By.CSS_SELECTOR, ".modal-header h2")
        self.assertIn("Add Room", title.text)

    def test_add_modal_has_fields(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        labels = [lbl.text for lbl in content.find_elements(By.TAG_NAME, "label")]
        self.assertTrue(any("Room Name" in l or "Name" in l for l in labels))
        self.assertTrue(any("Capacity" in l for l in labels))

    def test_add_modal_cancel_closes(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        self._click(By.CSS_SELECTOR, ".modal-footer .btn-secondary")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))

    # ── CRUD cycle ────────────────────────────────────────────────────────────

    def test_create_edit_delete_room(self):
        """Full CRUD: create a room, edit it, then delete it."""
        room_name = f"E2E Room {UNIQUE}"
        edited_name = f"E2E Edited Room {UNIQUE}"

        # CREATE
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        inputs = self.driver.find_elements(By.CSS_SELECTOR, ".modal-content input")
        inputs[0].send_keys(room_name)
        if len(inputs) > 1:
            inputs[1].clear()
            inputs[1].send_keys("10")
        self._click(By.CSS_SELECTOR, ".modal-footer button[type='submit']")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))
        time.sleep(1)

        # Search for the new room
        self._find(By.CSS_SELECTOR, ".table-search-input").clear()
        self._find(By.CSS_SELECTOR, ".table-search-input").send_keys(room_name)
        time.sleep(1)
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        self.assertGreaterEqual(len(rows), 1, "Created room not found in table")

        # EDIT
        edit_btn = self._find(By.CSS_SELECTOR, ".actions-cell .btn-icon")
        edit_btn.click()
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        name_input = self.driver.find_elements(By.CSS_SELECTOR, ".modal-content input")[0]
        name_input.clear()
        name_input.send_keys(edited_name)
        self._click(By.CSS_SELECTOR, ".modal-footer button[type='submit']")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))
        time.sleep(1)

        # DELETE
        self._find(By.CSS_SELECTOR, ".table-search-input").clear()
        self._find(By.CSS_SELECTOR, ".table-search-input").send_keys(edited_name)
        time.sleep(1)
        del_btn = self._find(By.CSS_SELECTOR, ".actions-cell .btn-icon--danger")
        del_btn.click()
        self._dismiss_alert_if_present()
        time.sleep(1)


if __name__ == "__main__":
    import unittest
    unittest.main()
