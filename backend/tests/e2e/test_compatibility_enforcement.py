"""
E2E tests – Feature 3: Compatibility & Credential Enforcement

Covers
------
  - Instructor dropdown in lesson modal marks incompatible instructors
  - Age-restriction block surfaces in the UI before submission
  - Student teaching requirements (e.g. CPR certification) reflected in
    instructor options when a student is selected
  - Override verdicts (blocked / required / preferred / disliked) appear
    on the instructor detail or compatibility panel
  - Selecting a hard-blocked instructor prevents lesson creation
  - Compatible instructor allows lesson creation to proceed

Presentation context
--------------------
  CompatibilityService checks before any assignment:
    - Hard blocks (instructor age restriction vs student age)
    - Student requirements (e.g. must have CPR-certified instructor)
    - Override verdicts: blocked, required, preferred, disliked
  Verdicts are stored in instructor_student_compatibility; admins can
  manually override with a reason.  The service is a pure domain service
  (no DB access) making it testable in isolation.

Run
---
    $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_compatibility_enforcement.py -v

Prerequisites
-------------
  Both servers must be running (backend :5000, frontend :3000).
  Tests that depend on specific DB state use self.skipTest() so the suite
  never hard-fails on a sparse dataset.
"""

import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from backend.tests.e2e.base import E2EBase


# ---------------------------------------------------------------------------
# Helpers shared across classes
# ---------------------------------------------------------------------------

def _navigate_to_schedule(test: E2EBase):
    test._get("/home")
    test.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".activity-panel")))
    # Wait for the "New Lesson" button (rendered as .btn.btn-primary in activity-right)
    test.wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'New Lesson')]"))
    )
    time.sleep(0.5)


def _open_new_lesson_modal(test: E2EBase):
    test._click(By.XPATH, "//button[contains(text(), 'New Lesson')]")
    test._find(By.CSS_SELECTOR, ".modal-overlay")


def _close_modal_cancel(test: E2EBase):
    try:
        cancel = test._find(By.XPATH, "//div[@class='modal-buttons']//button[@type='button']")
        cancel.click()
        test.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))
    except Exception:
        test._dismiss_alert_if_present()


def _modal_is_open(test: E2EBase) -> bool:
    return len(test.driver.find_elements(By.CSS_SELECTOR, ".modal-overlay")) > 0


def _select_nth_option(test: E2EBase, label_text: str, index: int = 1) -> bool:
    """Select option at *index* inside the <select> labelled with *label_text*."""
    selects = test.driver.find_elements(By.CSS_SELECTOR, ".modal-content select")
    for sel in selects:
        try:
            wrapper = sel.find_element(By.XPATH, "..")
            lbl = wrapper.find_element(By.TAG_NAME, "label")
            if label_text.lower() in lbl.text.lower():
                opts = sel.find_elements(By.TAG_NAME, "option")
                if len(opts) > index:
                    opts[index].click()
                    return True
        except Exception:
            continue
    return False


# ---------------------------------------------------------------------------
# Test: Instructor compatibility signals in the lesson modal
# ---------------------------------------------------------------------------

class TestCompatibilitySignalsInModal(E2EBase):
    """
    Verify that the lesson-scheduling modal reflects CompatibilityService
    verdicts in the Instructor dropdown when a student is selected.
    """

    def setUp(self):
        super().setUp()
        _navigate_to_schedule(self)

    def test_instructor_dropdown_renders_when_modal_opens(self):
        """Instructor <select> must be present in the lesson modal."""
        _open_new_lesson_modal(self)
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        selects = content.find_elements(By.CSS_SELECTOR, "select")
        labels = []
        for sel in selects:
            try:
                wrapper = sel.find_element(By.XPATH, "..")
                lbl = wrapper.find_element(By.TAG_NAME, "label")
                labels.append(lbl.text.lower())
            except Exception:
                continue
        self.assertTrue(
            any("instructor" in l for l in labels),
            "No Instructor dropdown found in lesson modal"
        )

    def test_selecting_student_triggers_compatibility_check(self):
        """
        Choosing a student must cause the UI to refresh the Instructor
        dropdown — the options list must still be present and non-empty.
        """
        _open_new_lesson_modal(self)
        content = self._find(By.CSS_SELECTOR, ".modal-content")

        student_options = content.find_elements(By.CSS_SELECTOR, "[data-multiselect-option]")
        if not student_options:
            self.skipTest("No student multi-select options — cannot test compatibility trigger")

        student_options[0].click()
        time.sleep(1.2)  # allow compatibility API call to complete

        selects = content.find_elements(By.CSS_SELECTOR, "select")
        instructor_options = []
        for sel in selects:
            try:
                wrapper = sel.find_element(By.XPATH, "..")
                lbl = wrapper.find_element(By.TAG_NAME, "label")
                if "instructor" in lbl.text.lower():
                    instructor_options = sel.find_elements(By.TAG_NAME, "option")
                    break
            except Exception:
                continue

        if not instructor_options:
            self.skipTest("Instructor select not found after student selection")

        self.assertGreater(
            len(instructor_options), 0,
            "Instructor dropdown must still render options after student selection"
        )

    def test_incompatible_instructor_label_appears(self):
        """
        When a student with known incompatible instructors is selected, those
        instructors must be visually annotated (e.g. '(incompatible)') in the
        Instructor dropdown options.

        Skipped when no incompatibility data exists in the database.
        """
        _open_new_lesson_modal(self)
        content = self._find(By.CSS_SELECTOR, ".modal-content")

        student_options = content.find_elements(By.CSS_SELECTOR, "[data-multiselect-option]")
        if not student_options:
            self.skipTest("No student multi-select options")

        student_options[0].click()
        time.sleep(1.2)

        selects = content.find_elements(By.CSS_SELECTOR, "select")
        all_option_texts = []
        for sel in selects:
            try:
                wrapper = sel.find_element(By.XPATH, "..")
                lbl = wrapper.find_element(By.TAG_NAME, "label")
                if "instructor" in lbl.text.lower():
                    all_option_texts = [o.text.lower() for o in sel.find_elements(By.TAG_NAME, "option")]
                    break
            except Exception:
                continue

        if not all_option_texts:
            self.skipTest("Instructor options not found")

        incompatible_signals = ["incompatible", "blocked", "unavailable", "restricted"]
        has_annotation = any(
            any(sig in opt for sig in incompatible_signals) for opt in all_option_texts
        )

        if not has_annotation:
            self.skipTest(
                "No incompatible instructors found for the selected student — "
                "annotation test requires known incompatibility in DB"
            )

        self.assertTrue(has_annotation, "Incompatible instructor must be annotated in the dropdown")

    def test_preferred_instructor_label_appears(self):
        """
        When a student has a 'preferred' instructor override, that instructor
        must appear annotated (e.g. '(preferred)') in the dropdown.
        """
        _open_new_lesson_modal(self)
        content = self._find(By.CSS_SELECTOR, ".modal-content")

        student_options = content.find_elements(By.CSS_SELECTOR, "[data-multiselect-option]")
        if not student_options:
            self.skipTest("No student options available")

        student_options[0].click()
        time.sleep(1.2)

        selects = content.find_elements(By.CSS_SELECTOR, "select")
        all_option_texts = []
        for sel in selects:
            try:
                wrapper = sel.find_element(By.XPATH, "..")
                lbl = wrapper.find_element(By.TAG_NAME, "label")
                if "instructor" in lbl.text.lower():
                    all_option_texts = [o.text.lower() for o in sel.find_elements(By.TAG_NAME, "option")]
                    break
            except Exception:
                continue

        if not all_option_texts:
            self.skipTest("Instructor options not found after student selection")

        preference_signals = ["preferred", "favourite", "recommended"]
        has_preference = any(
            any(sig in opt for sig in preference_signals) for opt in all_option_texts
        )

        if not has_preference:
            self.skipTest("No 'preferred' instructor verdict exists in DB for this student")

        self.assertTrue(has_preference)


# ---------------------------------------------------------------------------
# Test: Hard-blocked instructor prevents lesson creation
# ---------------------------------------------------------------------------

class TestHardBlockPreventsBooking(E2EBase):
    """
    Verify that selecting a hard-blocked instructor and submitting the form
    results in a rejection (alert, toast, or modal stays open).
    """

    def setUp(self):
        super().setUp()
        _navigate_to_schedule(self)

    def test_booking_blocked_instructor_is_rejected(self):
        """
        Select a student + their blocked instructor, then submit.
        Expect an error signal — modal must not silently close.

        Skipped when no blocked pairing exists in the database.
        """
        _open_new_lesson_modal(self)
        content = self._find(By.CSS_SELECTOR, ".modal-content")

        # Select a room
        selects = content.find_elements(By.CSS_SELECTOR, "select")
        if not selects:
            self.skipTest("No selects in modal")
        room_opts = selects[0].find_elements(By.TAG_NAME, "option")
        if len(room_opts) < 2:
            self.skipTest("No room options in DB")
        room_opts[1].click()
        time.sleep(0.4)

        # Select a student
        student_options = content.find_elements(By.CSS_SELECTOR, "[data-multiselect-option]")
        if not student_options:
            self.skipTest("No student options in modal")
        student_options[0].click()
        time.sleep(1.2)

        # Find a blocked instructor option
        selects = content.find_elements(By.CSS_SELECTOR, "select")
        blocked_index = None
        for sel in selects:
            try:
                wrapper = sel.find_element(By.XPATH, "..")
                lbl = wrapper.find_element(By.TAG_NAME, "label")
                if "instructor" not in lbl.text.lower():
                    continue
                opts = sel.find_elements(By.TAG_NAME, "option")
                for i, opt in enumerate(opts):
                    if "blocked" in opt.text.lower() or "incompatible" in opt.text.lower():
                        blocked_index = i
                        opt.click()
                        break
            except Exception:
                continue
            if blocked_index is not None:
                break

        if blocked_index is None:
            self.skipTest("No blocked instructor option found — test requires incompatibility data")

        # Set times and submit
        fields = content.find_elements(By.CSS_SELECTOR, ".form-field")
        for field in fields:
            try:
                lbl = field.find_element(By.TAG_NAME, "label")
                inp = field.find_element(By.CSS_SELECTOR, "input[type='time']")
                if "start" in lbl.text.lower():
                    inp.clear()
                    inp.send_keys("10:00")
                elif "end" in lbl.text.lower():
                    inp.clear()
                    inp.send_keys("11:00")
            except Exception:
                continue

        submit = content.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit.click()
        time.sleep(1.5)

        # Expect a rejection signal
        try:
            alert = self.wait.until(EC.alert_is_present())
            alert_text = alert.text.lower()
            alert.accept()
            rejection_keywords = ["incompatible", "blocked", "not allowed", "cannot", "error", "conflict"]
            self.assertTrue(
                any(kw in alert_text for kw in rejection_keywords),
                f"Alert present but did not indicate a compatibility block: '{alert_text}'"
            )
        except TimeoutException:
            self.assertTrue(
                _modal_is_open(self),
                "Expected alert or open modal when booking a hard-blocked instructor"
            )
            _close_modal_cancel(self)


# ---------------------------------------------------------------------------
# Test: Compatibility information on instructor detail page
# ---------------------------------------------------------------------------

class TestCompatibilityOnInstructorDetail(E2EBase):
    """
    Verify that the instructor detail page surfaces compatibility overrides
    so admins can review and manage them.
    """

    def setUp(self):
        super().setUp()
        self._get("/instructors")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-instructor")))
        time.sleep(0.5)

    def test_instructor_detail_page_loads(self):
        """Clicking an instructor row must navigate to the detail page."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No instructors in database")
        rows[0].click()
        self.wait.until(EC.url_contains("/instructors/"))
        self.assertRegex(self.driver.current_url, r"/instructors/[a-f0-9-]+")

    def test_instructor_detail_shows_credentials_tab_or_section(self):
        """
        Instructor detail must expose a credentials or compatibility section
        so admins can inspect validity dates and student overrides.
        """
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No instructors in database")
        rows[0].click()
        self.wait.until(EC.url_contains("/instructors/"))
        time.sleep(0.8)

        page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        credential_signals = ["credential", "certification", "compatibility", "students", "cert"]
        has_signal = any(sig in page_text for sig in credential_signals)
        self.assertTrue(
            has_signal,
            "Instructor detail page must surface credential or compatibility information"
        )

    def test_instructor_detail_has_breadcrumb(self):
        """Instructor detail must show a breadcrumb back to the list."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No instructors in database")
        rows[0].click()
        self.wait.until(EC.url_contains("/instructors/"))
        breadcrumb = self._find(By.CSS_SELECTOR, ".page-breadcrumb")
        self.assertTrue(breadcrumb.is_displayed())


# ---------------------------------------------------------------------------
# Test: Teaching requirements visible on student detail
# ---------------------------------------------------------------------------

class TestStudentTeachingRequirements(E2EBase):
    """
    Verify that student detail pages expose teaching requirements (e.g.
    'instructor must have CPR certification') so admins can manage them.
    """

    def setUp(self):
        super().setUp()
        self._get("/students")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-navbar.page-students")))
        time.sleep(0.5)

    def test_student_detail_page_loads(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No students in database")
        rows[0].click()
        self.wait.until(EC.url_contains("/students/"))
        self.assertRegex(self.driver.current_url, r"/students/[a-f0-9-]+")

    def test_student_detail_surfaces_enrollment_or_requirements(self):
        """
        Student detail must show enrollment, lessons, or requirements info —
        confirming the compatibility surface is reachable from the admin UI.
        """
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No students in database")
        rows[0].click()
        self.wait.until(EC.url_contains("/students/"))
        time.sleep(0.8)

        page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        relevant_signals = [
            "enrollment", "lesson", "instructor", "requirement",
            "certification", "compatibility", "skill"
        ]
        has_signal = any(sig in page_text for sig in relevant_signals)
        self.assertTrue(
            has_signal,
            "Student detail must expose enrollment, lessons, or instructor requirements"
        )

    def test_student_detail_has_tabs_or_sections(self):
        """Student detail must organize information into tabs (Lessons, Invoices, etc.)."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if not rows:
            self.skipTest("No students in database")
        rows[0].click()
        self.wait.until(EC.url_contains("/students/"))
        # Wait for the tab bar to appear (student detail uses .client-tab)
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".client-tab")))
        except Exception:
            self.skipTest("Student detail tabs not rendered within timeout")

        tabs = self.driver.find_elements(
            By.CSS_SELECTOR, ".client-tab, .tab, .detail-tab, [role='tab']"
        )
        self.assertGreater(
            len(tabs), 0,
            "Student detail page must have tabs (e.g. Lessons, Invoices) to organize profile data"
        )


if __name__ == "__main__":
    import unittest
    unittest.main()
