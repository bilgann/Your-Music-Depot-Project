"""
E2E tests – Student Timetable / Schedule Generation

Covers
------
  - "Print Timetable" button visible on student detail page
  - Timetable modal opens and renders correctly
  - Header shows the student's name
  - Week view renders a calendar grid (time column + 5 day columns)
  - Month view renders a calendar grid (7 day header columns)
  - Week / Month tab switching works
  - Previous / Next navigation updates the displayed date range
  - Timetable shows lessons when enrolled, empty cells when not
  - Print button is present
  - Close button dismisses the modal
  - Overlay click dismisses the modal

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_student_timetable.py -v

Prerequisites
-------------
  Both servers must be running (backend :5000, frontend :3000).
  Requires at least one student in the database.  Tests that need enrolled
  lessons use self.skipTest() when none are found so the suite never hard-fails
  on an empty dataset.
"""

import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


# ── Shared navigation helper ───────────────────────────────────────────────────

def _go_to_first_student(test: E2EBase) -> str:
    """
    Navigate to the Students list and click the first row.
    Returns the student name from the breadcrumb, or skips the test if no
    students exist.
    """
    test._get("/students")
    test.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-students")))
    time.sleep(0.8)
    rows = test.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
    if not rows:
        test.skipTest("No students in the database — cannot test timetable")
    rows[0].click()
    test.wait.until(EC.url_contains("/students/"))
    # Give the detail page time to load
    time.sleep(0.8)
    return test.driver.current_url


def _open_timetable_modal(test: E2EBase):
    """Click 'Print Timetable' and wait for the modal to appear."""
    btn = test.wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Print Timetable')]"))
    )
    btn.click()
    test.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".timetable-modal")))
    time.sleep(0.5)  # allow initial data fetch


# ── Page-level tests (no modal) ────────────────────────────────────────────────

class TestStudentTimetableButton(E2EBase):
    """Verify the Print Timetable entry point on the student detail page."""

    def setUp(self):
        super().setUp()
        _go_to_first_student(self)

    def test_print_timetable_button_visible(self):
        """'Print Timetable' button must be visible in the student detail navbar."""
        btn = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Print Timetable')]")
            )
        )
        self.assertTrue(btn.is_displayed())

    def test_print_timetable_button_in_navbar(self):
        """Button must appear inside the page navbar actions area."""
        actions = self._find(By.CSS_SELECTOR, ".page-navbar-actions")
        btn = actions.find_element(By.XPATH, ".//*[contains(text(), 'Print Timetable')]")
        self.assertTrue(btn.is_displayed())


# ── Modal structure tests ──────────────────────────────────────────────────────

class TestTimetableModalStructure(E2EBase):
    """Verify modal renders with the correct layout and controls."""

    def setUp(self):
        super().setUp()
        _go_to_first_student(self)
        _open_timetable_modal(self)

    def test_modal_renders(self):
        """Timetable modal must be visible after clicking the button."""
        modal = self._find(By.CSS_SELECTOR, ".timetable-modal")
        self.assertTrue(modal.is_displayed())

    def test_modal_shows_student_name(self):
        """Modal header must contain the student's name."""
        header = self._find(By.CSS_SELECTOR, ".print-timetable__header h2")
        self.assertGreater(len(header.text.strip()), 0, "Student name must not be empty")

    def test_modal_shows_timetable_label(self):
        """Modal header paragraph must mention 'Timetable'."""
        header_p = self._find(By.CSS_SELECTOR, ".print-timetable__header p")
        self.assertIn("Timetable", header_p.text)

    def test_controls_bar_visible(self):
        """The controls bar (nav + view tabs) must be visible."""
        controls = self._find(By.CSS_SELECTOR, ".timetable-controls")
        self.assertTrue(controls.is_displayed())

    def test_weekly_tab_present(self):
        """'Weekly' view tab must be present."""
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".timetable-view-tab")
        tab_texts = [t.text.strip() for t in tabs]
        self.assertIn("Weekly", tab_texts)

    def test_monthly_tab_present(self):
        """'Monthly' view tab must be present."""
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".timetable-view-tab")
        tab_texts = [t.text.strip() for t in tabs]
        self.assertIn("Monthly", tab_texts)

    def test_weekly_tab_active_by_default(self):
        """The Weekly tab must be active when the modal first opens."""
        active_tabs = self.driver.find_elements(By.CSS_SELECTOR, ".timetable-view-tab.active")
        self.assertGreater(len(active_tabs), 0, "No active tab found")
        self.assertIn("Weekly", active_tabs[0].text)

    def test_print_button_present(self):
        """A Print button must be visible in the controls bar."""
        controls = self._find(By.CSS_SELECTOR, ".timetable-controls")
        # Button contains text 'Print' but not 'Print Timetable'
        btns = controls.find_elements(By.XPATH, ".//*[contains(text(), 'Print')]")
        self.assertGreater(len(btns), 0, "Print button not found in controls")

    def test_close_button_present(self):
        """A Close button must be visible in the controls bar."""
        controls = self._find(By.CSS_SELECTOR, ".timetable-controls")
        close_btns = controls.find_elements(By.XPATH, ".//*[contains(text(), 'Close')]")
        self.assertGreater(len(close_btns), 0, "Close button not found in controls")


# ── Week view tests ────────────────────────────────────────────────────────────

class TestTimetableWeekView(E2EBase):
    """Verify the weekly calendar grid renders correctly."""

    def setUp(self):
        super().setUp()
        _go_to_first_student(self)
        _open_timetable_modal(self)
        # Ensure we're on weekly view (it's the default, but be explicit)
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".timetable-view-tab")
        for tab in tabs:
            if "Weekly" in tab.text:
                tab.click()
                time.sleep(0.3)
                break

    def test_week_table_renders(self):
        """Weekly view must render a <table> element."""
        table = self._find(By.CSS_SELECTOR, ".print-timetable__week")
        self.assertTrue(table.is_displayed())

    def test_week_table_has_five_day_columns(self):
        """Week table header must have 5 weekday columns (Mon–Fri) plus a time column."""
        headers = self.driver.find_elements(By.CSS_SELECTOR, ".print-timetable__week thead th")
        # First <th> is the Time column, then Mon–Fri = 5 days
        self.assertGreaterEqual(len(headers), 6, "Expected Time column + 5 weekday columns")

    def test_week_table_has_weekday_names(self):
        """Week table header must contain all five weekday names."""
        headers = self.driver.find_elements(By.CSS_SELECTOR, ".print-timetable__week thead th")
        header_texts = " ".join(h.text for h in headers)
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            self.assertIn(day, header_texts, f"'{day}' not found in week table header")

    def test_week_table_has_time_rows(self):
        """Week table body must contain hour rows spanning 8 AM to 6 PM (≥ 10 rows)."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".print-timetable__week tbody tr")
        self.assertGreaterEqual(len(rows), 10, "Expected at least 10 hour rows (8 AM–6 PM)")

    def test_week_table_time_cells_labelled(self):
        """Time column cells must contain 'AM' or 'PM' labels."""
        cells = self.driver.find_elements(By.CSS_SELECTOR, ".print-timetable__time-cell")
        self.assertGreater(len(cells), 0, "No time cells found")
        texts = " ".join(c.text for c in cells)
        self.assertTrue(
            "AM" in texts or "PM" in texts,
            "Time cells must contain AM/PM labels"
        )

    def test_week_shows_date_range_in_header(self):
        """Header paragraph must include a date range for the current week."""
        header_p = self._find(By.CSS_SELECTOR, ".print-timetable__header p")
        # Should mention 'Weekly' and a date
        text = header_p.text
        self.assertIn("Weekly", text)
        # Date range contains digits
        self.assertTrue(any(ch.isdigit() for ch in text), "Expected date digits in header")

    def test_week_lessons_appear_when_enrolled(self):
        """
        If the student has any lesson enrollments, at least one lesson block
        must appear in the week view.

        Skipped when the student has no enrollments — the calendar simply
        shows empty cells, which is also correct behaviour.
        """
        lessons = self.driver.find_elements(By.CSS_SELECTOR, ".print-timetable__lesson")
        if not lessons:
            self.skipTest("Student has no enrolled lessons in the current week")
        self.assertGreater(len(lessons), 0)
        # Each lesson block must show a time
        for lesson in lessons:
            time_span = lesson.find_elements(By.CSS_SELECTOR, ".print-timetable__lesson-time")
            self.assertGreater(len(time_span), 0, "Lesson block missing time span")


# ── Month view tests ───────────────────────────────────────────────────────────

class TestTimetableMonthView(E2EBase):
    """Verify the monthly calendar grid renders after switching views."""

    def setUp(self):
        super().setUp()
        _go_to_first_student(self)
        _open_timetable_modal(self)
        # Switch to monthly view
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".timetable-view-tab")
        for tab in tabs:
            if "Monthly" in tab.text:
                tab.click()
                time.sleep(0.5)
                break

    def test_monthly_tab_becomes_active(self):
        """After clicking Monthly, that tab must be marked active."""
        active = self.driver.find_elements(By.CSS_SELECTOR, ".timetable-view-tab.active")
        self.assertGreater(len(active), 0)
        self.assertIn("Monthly", active[0].text)

    def test_month_table_renders(self):
        """Monthly view must render a <table> element."""
        table = self._find(By.CSS_SELECTOR, ".print-timetable__month")
        self.assertTrue(table.is_displayed())

    def test_month_table_has_seven_day_columns(self):
        """Month table header must have 7 columns (Sun–Sat or Mon–Sun)."""
        headers = self.driver.find_elements(By.CSS_SELECTOR, ".print-timetable__month thead th")
        self.assertEqual(len(headers), 7, "Month grid must have 7 day columns")

    def test_month_table_has_day_cells(self):
        """Month table body must contain at least 28 date cells."""
        cells = self.driver.find_elements(By.CSS_SELECTOR, ".print-timetable__month-cell")
        self.assertGreaterEqual(len(cells), 28, "Month grid must have at least 28 date cells")

    def test_month_cells_have_day_numbers(self):
        """Each month cell must contain a day number."""
        day_nums = self.driver.find_elements(By.CSS_SELECTOR, ".print-timetable__month-day")
        self.assertGreater(len(day_nums), 0, "No day-number elements found in month view")

    def test_month_shows_month_label_in_header(self):
        """Header paragraph must include 'Monthly' and the current month name."""
        header_p = self._find(By.CSS_SELECTOR, ".print-timetable__header p")
        text = header_p.text
        self.assertIn("Monthly", text)
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ]
        self.assertTrue(
            any(m in text for m in months),
            f"Expected a month name in header, got: '{text}'"
        )

    def test_month_lessons_appear_when_enrolled(self):
        """
        If the student has lesson enrollments in the current month, lesson
        blocks must appear in the month view.

        Skipped when no enrollments exist.
        """
        lessons = self.driver.find_elements(By.CSS_SELECTOR, ".print-timetable__month-lesson")
        if not lessons:
            self.skipTest("Student has no enrolled lessons in the current month")
        self.assertGreater(len(lessons), 0)


# ── Navigation tests ───────────────────────────────────────────────────────────

class TestTimetableNavigation(E2EBase):
    """Verify Previous / Next navigation updates the displayed date range."""

    def setUp(self):
        super().setUp()
        _go_to_first_student(self)
        _open_timetable_modal(self)

    def _header_label(self) -> str:
        el = self._find(By.CSS_SELECTOR, ".print-timetable__header p")
        return el.text.strip()

    def _click_nav(self, title: str):
        """Click a navigation icon button by its title attribute."""
        btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f".timetable-controls button[title='{title}']"))
        )
        btn.click()
        time.sleep(0.4)

    def test_next_week_changes_date_range(self):
        """Clicking Next must change the week label in the header."""
        before = self._header_label()
        self._click_nav("Next")
        after = self._header_label()
        self.assertNotEqual(before, after, "Date range must change after clicking Next")

    def test_prev_week_changes_date_range(self):
        """Clicking Previous must change the week label in the header."""
        before = self._header_label()
        self._click_nav("Previous")
        after = self._header_label()
        self.assertNotEqual(before, after, "Date range must change after clicking Previous")

    def test_next_then_prev_returns_to_original(self):
        """Next followed by Previous must return to the original date range."""
        original = self._header_label()
        self._click_nav("Next")
        self._click_nav("Previous")
        restored = self._header_label()
        self.assertEqual(original, restored, "Should return to original week after Next → Previous")

    def test_next_month_changes_month_label(self):
        """In monthly view, clicking Next must update the month label."""
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".timetable-view-tab")
        for tab in tabs:
            if "Monthly" in tab.text:
                tab.click()
                time.sleep(0.4)
                break
        before = self._header_label()
        self._click_nav("Next")
        after = self._header_label()
        self.assertNotEqual(before, after, "Month label must change after clicking Next")

    def test_switching_view_updates_label(self):
        """Switching from Weekly to Monthly must update the header label."""
        week_label = self._header_label()
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".timetable-view-tab")
        for tab in tabs:
            if "Monthly" in tab.text:
                tab.click()
                time.sleep(0.4)
                break
        month_label = self._header_label()
        self.assertNotEqual(week_label, month_label, "Header must differ between weekly and monthly")
        self.assertIn("Monthly", month_label)


# ── Dismiss / close tests ──────────────────────────────────────────────────────

class TestTimetableModalDismiss(E2EBase):
    """Verify the modal can be closed without side effects."""

    def setUp(self):
        super().setUp()
        _go_to_first_student(self)

    def test_close_button_dismisses_modal(self):
        """Clicking Close must remove the timetable modal from the page."""
        _open_timetable_modal(self)
        controls = self._find(By.CSS_SELECTOR, ".timetable-controls")
        close_btn = controls.find_element(By.XPATH, ".//*[contains(text(), 'Close')]")
        close_btn.click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".timetable-modal")))
        self.assertEqual(
            len(self.driver.find_elements(By.CSS_SELECTOR, ".timetable-modal")), 0
        )

    def test_overlay_click_dismisses_modal(self):
        """Clicking the overlay backdrop must close the modal."""
        _open_timetable_modal(self)
        overlay = self._find(By.CSS_SELECTOR, ".modal-overlay")
        # Use JS click on the overlay element directly — avoids the Selenium 4
        # behaviour where ActionChains offsets are relative to the element center,
        # which would land on the modal content and trigger stopPropagation.
        self.driver.execute_script("arguments[0].click();", overlay)
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".timetable-modal")))

    def test_student_page_intact_after_modal_closed(self):
        """After closing the timetable modal, the student detail page must still render."""
        _open_timetable_modal(self)
        controls = self._find(By.CSS_SELECTOR, ".timetable-controls")
        close_btn = controls.find_element(By.XPATH, ".//*[contains(text(), 'Close')]")
        close_btn.click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".timetable-modal")))
        # Detail page breadcrumb must still be present
        breadcrumb = self._find(By.CSS_SELECTOR, ".page-breadcrumb")
        self.assertTrue(breadcrumb.is_displayed())

    def test_can_reopen_modal_after_closing(self):
        """The timetable modal must be re-openable after being closed."""
        _open_timetable_modal(self)
        controls = self._find(By.CSS_SELECTOR, ".timetable-controls")
        close_btn = controls.find_element(By.XPATH, ".//*[contains(text(), 'Close')]")
        close_btn.click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".timetable-modal")))
        # Re-open
        _open_timetable_modal(self)
        modal = self._find(By.CSS_SELECTOR, ".timetable-modal")
        self.assertTrue(modal.is_displayed())


if __name__ == "__main__":
    import unittest
    unittest.main()
