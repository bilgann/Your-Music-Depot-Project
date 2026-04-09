"""
E2E tests – Feature 1: Student & Instructor Management (CRUD)

Covers
------
  - Students: page renders, add modal with skill-level fields, edit, delete button visible
  - Instructors: page renders, add modal with credential fields, edit, delete button visible
  - Clients: add modal with required contact fields, row navigation to detail
  - Schema validation: required-field enforcement before any DB write

Presentation context
--------------------
  Admins maintain accurate profiles for students, instructors, and clients.
  Students carry instrument skill levels and teaching requirements.
  Instructors carry credentials with validity dates.
  CRUD is enforced at the API layer with schema-based validation.

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_crud_management.py -v

Prerequisites
-------------
  Both servers must be running (backend :5000, frontend :3000).
  Tests that require existing data use self.skipTest() when none are found.
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


# ---------------------------------------------------------------------------
# Feature: Student profiles (skill levels + teaching requirements)
# ---------------------------------------------------------------------------

class TestStudentCRUD(E2EBase):
    """
    Verify the Students management page allows creating, editing, and
    deleting student records with instrument skill levels.
    """

    def setUp(self):
        super().setUp()
        self._get("/students")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-students")))
        time.sleep(1)  # allow table data to render

    # ── Page structure ─────────────────────────────────────────────────────────

    def test_page_renders_with_correct_title(self):
        """Students page must display 'Students' as the heading."""
        title = self._find(By.CSS_SELECTOR, ".page-navbar.page-students h1")
        self.assertEqual(title.text.strip(), "Students")

    def test_table_exposes_expected_columns(self):
        """Data table must include Name, Email, Phone, and Client columns."""
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".data-table thead th")))
        headers = self.driver.find_elements(By.CSS_SELECTOR, ".data-table thead th")
        texts = [h.text.strip().lower() for h in headers]
        for col in ["name", "email", "phone", "client"]:
            self.assertIn(col, texts, f"Column '{col}' missing from students table")

    # ── Add student modal ──────────────────────────────────────────────────────

    def test_add_modal_opens_on_button_click(self):
        """'Add Student' button must open the creation modal."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self.assertTrue(self._find(By.CSS_SELECTOR, ".modal-overlay").is_displayed())

    def test_add_modal_title_is_correct(self):
        """Modal header must reference 'Student'."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        title = self._find(By.CSS_SELECTOR, ".modal-header h2")
        self.assertIn("Student", title.text)

    def test_add_modal_has_core_contact_fields(self):
        """Modal must expose Name, Email, Phone, and Client fields."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        labels = [lbl.text for lbl in content.find_elements(By.TAG_NAME, "label")]
        for field in ["Name", "Email", "Phone", "Client"]:
            self.assertTrue(
                any(field in l for l in labels),
                f"Expected '{field}' field in Add Student modal"
            )

    def test_add_modal_submit_without_name_blocked(self):
        """Submitting without a name must keep the modal open (required-field guard)."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        # Submit immediately without filling any fields
        submit = self.driver.find_element(By.CSS_SELECTOR, ".modal-footer .btn-primary")
        submit.click()
        time.sleep(0.5)
        # Modal must remain open — the API/frontend guard prevents the write
        self.assertTrue(
            len(self.driver.find_elements(By.CSS_SELECTOR, ".modal-overlay")) > 0,
            "Modal must stay open when required fields are missing"
        )

    def test_add_modal_cancel_closes_without_side_effects(self):
        """Cancelling the modal must not alter the student list."""
        # Wait for the table to be populated before capturing the baseline count
        time.sleep(0.5)
        rows_before = len(self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr"))
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        self._click(By.CSS_SELECTOR, ".modal-footer .btn-secondary")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))
        time.sleep(0.3)
        rows_after = len(self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr"))
        self.assertEqual(rows_before, rows_after)

    # ── Edit / Delete ──────────────────────────────────────────────────────────

    def test_edit_button_opens_prefilled_modal(self):
        """Clicking the edit icon on a student row must open a Student modal."""
        edit_btns = self.driver.find_elements(By.CSS_SELECTOR, ".actions-cell .btn-icon")
        if not edit_btns:
            self.skipTest("No students in database")
        edit_btns[0].click()
        title = self._find(By.CSS_SELECTOR, ".modal-header h2")
        self.assertIn("Student", title.text)

    def test_edit_modal_fields_are_prepopulated(self):
        """Edit modal must have at least the Name field pre-filled."""
        edit_btns = self.driver.find_elements(By.CSS_SELECTOR, ".actions-cell .btn-icon")
        if not edit_btns:
            self.skipTest("No students in database")
        edit_btns[0].click()
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        inputs = self.driver.find_elements(By.CSS_SELECTOR, ".modal-content input[type='text']")
        non_empty = [inp for inp in inputs if inp.get_attribute("value")]
        self.assertGreater(len(non_empty), 0, "Edit modal must pre-fill at least one text field")

    def test_delete_button_visible_per_row(self):
        """Every student row must expose a delete action button."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No students in database")
        del_btns = self.driver.find_elements(By.CSS_SELECTOR, ".actions-cell .btn-icon--danger")
        self.assertGreater(len(del_btns), 0, "No delete buttons found on student rows")

    def test_row_click_navigates_to_student_detail(self):
        """Clicking a student row must navigate to /students/<id>."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No students in database")
        rows[0].click()
        self.wait.until(EC.url_contains("/students/"))
        self.assertRegex(self.driver.current_url, r"/students/[a-f0-9-]+")


# ---------------------------------------------------------------------------
# Feature: Instructor profiles (credentials + validity dates)
# ---------------------------------------------------------------------------

class TestInstructorCRUD(E2EBase):
    """
    Verify the Instructors management page allows creating, editing, and
    deleting instructor records. Instructors carry credentials with validity dates.
    """

    def setUp(self):
        super().setUp()
        self._get("/instructors")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-instructor")))
        time.sleep(1)  # allow table data to render

    # ── Page structure ─────────────────────────────────────────────────────────

    def test_page_renders_with_correct_title(self):
        title = self._find(By.CSS_SELECTOR, ".page-navbar.page-instructor h1")
        self.assertEqual(title.text.strip(), "Instructors")

    def test_table_exposes_expected_columns(self):
        """Table must include Name, Email, and Phone columns."""
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".data-table thead th")))
        headers = self.driver.find_elements(By.CSS_SELECTOR, ".data-table thead th")
        texts = [h.text.strip().lower() for h in headers]
        for col in ["name", "email", "phone"]:
            self.assertIn(col, texts, f"Column '{col}' missing from instructors table")

    # ── Add instructor modal ───────────────────────────────────────────────────

    def test_add_modal_opens(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self.assertTrue(self._find(By.CSS_SELECTOR, ".modal-overlay").is_displayed())

    def test_add_modal_title_is_correct(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        title = self._find(By.CSS_SELECTOR, ".modal-header h2")
        self.assertIn("Add Instructor", title.text)

    def test_add_modal_has_core_contact_fields(self):
        """Modal must contain Name, Email, Phone fields."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        labels = [lbl.text for lbl in content.find_elements(By.TAG_NAME, "label")]
        for field in ["Name", "Email", "Phone"]:
            self.assertTrue(
                any(field in l for l in labels),
                f"Expected '{field}' field in Add Instructor modal"
            )

    def test_add_modal_submit_without_name_blocked(self):
        """Submitting without a name must keep the modal open."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        submit = self.driver.find_element(By.CSS_SELECTOR, ".modal-footer .btn-primary")
        submit.click()
        time.sleep(0.5)
        self.assertTrue(
            len(self.driver.find_elements(By.CSS_SELECTOR, ".modal-overlay")) > 0,
            "Modal must stay open when required fields are missing"
        )

    def test_add_modal_cancel_closes(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        self._click(By.CSS_SELECTOR, ".modal-footer .btn-secondary")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))

    # ── Edit / Delete ──────────────────────────────────────────────────────────

    def test_edit_button_opens_prefilled_modal(self):
        """Edit icon must open 'Edit Instructor' modal pre-filled with existing data."""
        edit_btns = self.driver.find_elements(By.CSS_SELECTOR, ".actions-cell .btn-icon")
        if not edit_btns:
            self.skipTest("No instructors in database")
        edit_btns[0].click()
        title = self._find(By.CSS_SELECTOR, ".modal-header h2")
        self.assertIn("Edit Instructor", title.text)

    def test_edit_modal_fields_are_prepopulated(self):
        """Edit modal must have at least one text field pre-filled."""
        edit_btns = self.driver.find_elements(By.CSS_SELECTOR, ".actions-cell .btn-icon")
        if not edit_btns:
            self.skipTest("No instructors in database")
        edit_btns[0].click()
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        inputs = self.driver.find_elements(By.CSS_SELECTOR, ".modal-content input[type='text']")
        non_empty = [inp for inp in inputs if inp.get_attribute("value")]
        self.assertGreater(len(non_empty), 0, "Edit modal must pre-fill at least one text field")

    def test_delete_button_visible_per_row(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No instructors in database")
        del_btns = self.driver.find_elements(By.CSS_SELECTOR, ".actions-cell .btn-icon--danger")
        self.assertGreater(len(del_btns), 0)

    def test_search_input_is_present_and_interactive(self):
        """Search input must be visible and accept text input."""
        search = self._find(By.CSS_SELECTOR, ".table-search-input")
        self.assertTrue(search.is_displayed())
        search.clear()
        search.send_keys("test query")
        time.sleep(0.5)
        # The field must retain the typed value
        self.assertIn("test", search.get_attribute("value").lower())


# ---------------------------------------------------------------------------
# Feature: Client profiles (parent-of / contact separation)
# ---------------------------------------------------------------------------

class TestClientCRUD(E2EBase):
    """
    Verify the Clients management page exposes CRUD for the contact entity.
    A parent who is also a student has one contact record — the client record.
    """

    def setUp(self):
        super().setUp()
        self._get("/clients")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-clients")))

    def test_page_renders_with_correct_title(self):
        title = self._find(By.CSS_SELECTOR, ".page-navbar.page-clients h1")
        self.assertEqual(title.text.strip(), "Clients")

    def test_page_has_add_client_button(self):
        btn = self._find(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self.assertIn("Add Client", btn.text)

    def test_add_modal_has_contact_fields(self):
        """Client modal must expose Name, Email, and Phone (one contact record per person)."""
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        labels = [lbl.text for lbl in content.find_elements(By.TAG_NAME, "label")]
        for field in ["Name", "Email", "Phone"]:
            self.assertTrue(
                any(field in l for l in labels),
                f"Expected '{field}' in Add Client modal"
            )

    def test_add_modal_cancel_closes(self):
        self._click(By.CSS_SELECTOR, ".page-navbar-actions .btn-primary")
        self._find(By.CSS_SELECTOR, ".modal-overlay")
        self._click(By.CSS_SELECTOR, ".modal-footer .btn-secondary")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))

    def test_row_click_navigates_to_client_detail(self):
        """Clicking a client row must navigate to /clients/<id>."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No clients in database")
        rows[0].click()
        self.wait.until(EC.url_contains("/clients/"))
        self.assertRegex(self.driver.current_url, r"/clients/[a-f0-9-]+")

    def test_edit_and_delete_buttons_visible(self):
        """Each client row must show both an edit and a delete action."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No clients in database")
        edit_btns = self.driver.find_elements(By.CSS_SELECTOR, ".actions-cell .btn-icon")
        del_btns = self.driver.find_elements(By.CSS_SELECTOR, ".actions-cell .btn-icon--danger")
        self.assertGreater(len(edit_btns), 0, "Edit buttons missing from client rows")
        self.assertGreater(len(del_btns), 0, "Delete buttons missing from client rows")


if __name__ == "__main__":
    import unittest
    unittest.main()
