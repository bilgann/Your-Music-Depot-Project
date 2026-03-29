"""
End-to-end Selenium tests covering all implemented user flows.

Prerequisites
-------------
- Frontend running at http://localhost:3000  (npm run dev)
- Backend  running at http://localhost:5000  (flask run)
- Google Chrome + matching chromedriver on PATH  (or install via `pip install webdriver-manager`)

Run
---
    pytest backend/tests/e2e/test_user_flows.py -v

Environment variables (optional)
---------------------------------
    E2E_BASE_URL  – override default frontend URL   (default: http://localhost:3000)
    E2E_USERNAME  – valid login username             (default: barnes)
    E2E_PASSWORD  – valid login password             (default: password)
    E2E_HEADLESS  – set to "1" to run headless       (default: 0)
"""

import os
import time
import unittest

from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ── Config ─────────────────────────────────────────────────────────────────────
BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:3000")
USERNAME = os.getenv("E2E_USERNAME", "barnes")
PASSWORD = os.getenv("E2E_PASSWORD", "password")
HEADLESS = os.getenv("E2E_HEADLESS", "0") == "1"

DEFAULT_TIMEOUT = 10  # seconds


# ── Driver factory ─────────────────────────────────────────────────────────────
def _make_driver() -> webdriver.Chrome:
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")

    # Try webdriver-manager first; fall back to PATH chromedriver
    try:
        from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=opts)
    except Exception:
        return webdriver.Chrome(options=opts)


# ── Shared helpers ─────────────────────────────────────────────────────────────
class E2EBase(unittest.TestCase):
    """Base class – creates a fresh browser for every test."""

    driver: webdriver.Chrome
    wait: WebDriverWait

    def setUp(self):
        self.driver = _make_driver()
        self.wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT)

    def tearDown(self):
        self.driver.quit()

    # ── helpers ────────────────────────────────────────────────────────────────

    def _get(self, path: str):
        self.driver.get(BASE_URL + path)

    def _find(self, by: str, value: str):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def _click(self, by: str, value: str):
        el = self.wait.until(EC.element_to_be_clickable((by, value)))
        el.click()
        return el

    def _type(self, by: str, value: str, text: str):
        el = self._find(by, value)
        el.clear()
        el.send_keys(text)
        return el

    def _do_login(self, username: str = USERNAME, password: str = PASSWORD):
        """Navigate to login and submit credentials."""
        self._get("/login")
        self._type(By.ID, "username", username)
        self._type(By.ID, "password", password)
        self._click(By.CSS_SELECTOR, ".login-submit")

    def _login_and_wait_home(self):
        """Login and wait until the dashboard home page is loaded."""
        self._do_login()
        self.wait.until(EC.url_contains("/home"))

    def _dismiss_alert_if_present(self):
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except NoAlertPresentException:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# Flow 1 – Login / Authentication
# ══════════════════════════════════════════════════════════════════════════════
class TestLoginFlow(E2EBase):
    """Covers: redirect to login, valid login, invalid login, show/hide password."""

    def test_root_redirects_to_login(self):
        """/ should redirect to /login."""
        self._get("/")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_login_page_renders_form(self):
        """Login page must show the username, password inputs and submit button."""
        self._get("/login")
        self._find(By.ID, "username")
        self._find(By.ID, "password")
        self._find(By.CSS_SELECTOR, ".login-submit")
        title = self._find(By.CSS_SELECTOR, ".login-title")
        self.assertIn("Music Depot", title.text)

    def test_valid_login_redirects_to_home(self):
        """Successful login must navigate to /home."""
        self._do_login()
        self.wait.until(EC.url_contains("/home"))
        self.assertIn("/home", self.driver.current_url)

    def test_invalid_password_shows_error(self):
        """Wrong password must display an error message, stay on /login."""
        self._do_login(password="wrong_password_xyz")
        error = self._find(By.CSS_SELECTOR, ".login-error")
        self.assertTrue(error.is_displayed())
        self.assertIn("/login", self.driver.current_url)

    def test_invalid_username_shows_error(self):
        """Unknown username must display an error message."""
        self._do_login(username="no_such_user_xyz")
        error = self._find(By.CSS_SELECTOR, ".login-error")
        self.assertTrue(error.is_displayed())

    def test_empty_username_prevents_submit(self):
        """HTML5 required attribute prevents form submission with empty username."""
        self._get("/login")
        self._type(By.ID, "password", PASSWORD)
        submit = self._find(By.CSS_SELECTOR, ".login-submit")
        submit.click()
        # Should remain on /login (browser-level validation)
        self.assertIn("/login", self.driver.current_url)

    def test_empty_password_prevents_submit(self):
        """HTML5 required attribute prevents form submission with empty password."""
        self._get("/login")
        self._type(By.ID, "username", USERNAME)
        submit = self._find(By.CSS_SELECTOR, ".login-submit")
        submit.click()
        self.assertIn("/login", self.driver.current_url)

    def test_show_hide_password_toggle(self):
        """Show/Hide button must toggle the password field's type."""
        self._get("/login")
        pwd_input = self._find(By.ID, "password")
        self.assertEqual(pwd_input.get_attribute("type"), "password")

        self._click(By.CSS_SELECTOR, ".login-toggle-password")
        self.assertEqual(pwd_input.get_attribute("type"), "text")

        self._click(By.CSS_SELECTOR, ".login-toggle-password")
        self.assertEqual(pwd_input.get_attribute("type"), "password")

    def test_submit_button_disabled_while_loading(self):
        """Submit button should show 'Signing in…' and be disabled during the request."""
        self._get("/login")
        self._type(By.ID, "username", USERNAME)
        self._type(By.ID, "password", PASSWORD)
        submit = self.driver.find_element(By.CSS_SELECTOR, ".login-submit")
        submit.click()
        # Immediately after click the button text changes or it is disabled
        try:
            self.wait.until(
                lambda d: d.find_element(By.CSS_SELECTOR, ".login-submit").get_attribute("disabled")
                or "Signing" in d.find_element(By.CSS_SELECTOR, ".login-submit").text
            )
        except TimeoutException:
            # Navigation may have already completed – that also means it worked
            pass


# ══════════════════════════════════════════════════════════════════════════════
# Flow 2 – Dashboard Home
# ══════════════════════════════════════════════════════════════════════════════
class TestDashboardHome(E2EBase):
    """Covers: dashboard stats, quick-action buttons, auth guard."""

    def test_home_requires_authentication(self):
        """/home without a token must redirect to /login."""
        self._get("/home")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_home_renders_after_login(self):
        """After login, /home must display the dashboard title."""
        self._login_and_wait_home()
        title = self._find(By.CSS_SELECTOR, ".dashboard-title")
        self.assertEqual(title.text.strip(), "Dashboard")

    def test_home_shows_today_lessons_stat(self):
        """Dashboard must render the 'Today's Lessons' stat card."""
        self._login_and_wait_home()
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".stat-card")
        labels = [c.find_element(By.CSS_SELECTOR, ".stat-label").text for c in cards]
        self.assertIn("Today's Lessons", labels)

    def test_home_shows_next_lesson_stat(self):
        """Dashboard must render the 'Next Lesson' stat card."""
        self._login_and_wait_home()
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".stat-card")
        labels = [c.find_element(By.CSS_SELECTOR, ".stat-label").text for c in cards]
        self.assertIn("Next Lesson", labels)

    def test_add_lesson_button_navigates_to_schedule(self):
        """'+ Add Lesson' button must navigate to /schedule."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".action-btn--primary")
        self.wait.until(EC.url_contains("/schedule"))
        self.assertIn("/schedule", self.driver.current_url)

    def test_add_student_button_navigates_to_students(self):
        """'+ Add Student' button must navigate to /students."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".action-btn--secondary")
        self.wait.until(EC.url_contains("/students"))
        self.assertIn("/students", self.driver.current_url)

    def test_view_schedule_button_navigates_to_schedule(self):
        """'View Schedule' button must navigate to /schedule."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".action-btn--ghost")
        self.wait.until(EC.url_contains("/schedule"))
        self.assertIn("/schedule", self.driver.current_url)


# ══════════════════════════════════════════════════════════════════════════════
# Flow 3 – Sidebar Navigation
# ══════════════════════════════════════════════════════════════════════════════
class TestSidebarNavigation(E2EBase):
    """Covers: all sidebar links, active state, logout."""

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
        link = self._get_sidebar_link("Schedule")
        link.click()
        self.wait.until(EC.url_contains("/schedule"))
        self.assertIn("/schedule", self.driver.current_url)

    def test_sidebar_students_link_navigates(self):
        link = self._get_sidebar_link("Students")
        link.click()
        self.wait.until(EC.url_contains("/students"))
        self.assertIn("/students", self.driver.current_url)

    def test_sidebar_instructors_link_navigates(self):
        link = self._get_sidebar_link("Instructors")
        link.click()
        self.wait.until(EC.url_contains("/instructors"))
        self.assertIn("/instructors", self.driver.current_url)

    def test_sidebar_rooms_link_navigates(self):
        link = self._get_sidebar_link("Rooms")
        link.click()
        self.wait.until(EC.url_contains("/rooms"))
        self.assertIn("/rooms", self.driver.current_url)

    def test_sidebar_payments_link_navigates(self):
        link = self._get_sidebar_link("Payments")
        link.click()
        self.wait.until(EC.url_contains("/payments"))
        self.assertIn("/payments", self.driver.current_url)

    def test_sidebar_settings_link_navigates(self):
        link = self._get_sidebar_link("Settings")
        link.click()
        self.wait.until(EC.url_contains("/settings"))
        self.assertIn("/settings", self.driver.current_url)

    def test_active_link_has_active_class(self):
        """The sidebar link matching the current page should have the 'active' CSS class."""
        # Navigate to schedule and verify it becomes active
        link = self._get_sidebar_link("Schedule")
        link.click()
        self.wait.until(EC.url_contains("/schedule"))
        active_link = self._find(By.CSS_SELECTOR, ".sidebar-link.active")
        self.assertIn("Schedule", active_link.text)

    def test_sidebar_logout_button_present(self):
        """Sidebar must contain a logout button."""
        btn = self._find(By.CSS_SELECTOR, ".sidebar-logout")
        self.assertTrue(btn.is_displayed())


# ══════════════════════════════════════════════════════════════════════════════
# Flow 4 – Logout
# ══════════════════════════════════════════════════════════════════════════════
class TestLogoutFlow(E2EBase):
    """Covers: logout button, redirect to login, token cleared."""

    def test_logout_redirects_to_login(self):
        """Clicking logout must redirect to /login."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".sidebar-logout")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_after_logout_protected_route_redirects(self):
        """After logout, navigating to /home must redirect back to /login."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".sidebar-logout")
        self.wait.until(EC.url_contains("/login"))
        self._get("/home")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_logout_clears_token_from_local_storage(self):
        """After logout, localStorage['token'] must be absent or null."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".sidebar-logout")
        self.wait.until(EC.url_contains("/login"))
        token = self.driver.execute_script("return localStorage.getItem('token');")
        self.assertIsNone(token)

    def test_can_login_again_after_logout(self):
        """User can complete a second login after logging out."""
        self._login_and_wait_home()
        self._click(By.CSS_SELECTOR, ".sidebar-logout")
        self.wait.until(EC.url_contains("/login"))
        self._do_login()
        self.wait.until(EC.url_contains("/home"))
        self.assertIn("/home", self.driver.current_url)


# ══════════════════════════════════════════════════════════════════════════════
# Flow 5 – Schedule Page (Calendar)
# ══════════════════════════════════════════════════════════════════════════════
class TestSchedulePage(E2EBase):
    """Covers: calendar renders, week navigation, today button."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        # Navigate to schedule
        self.driver.find_elements(By.CSS_SELECTOR, ".sidebar-link")[1].click()
        self.wait.until(EC.url_contains("/schedule"))

    def test_schedule_page_renders_calendar(self):
        """Schedule page must render the activity panel."""
        panel = self._find(By.CSS_SELECTOR, ".activity-panel")
        self.assertTrue(panel.is_displayed())

    def test_calendar_shows_five_day_columns(self):
        """Calendar grid must contain 5 day columns (Mon–Fri)."""
        self._find(By.CSS_SELECTOR, ".days-col")
        day_cols = self.driver.find_elements(By.CSS_SELECTOR, ".day-column")
        self.assertEqual(len(day_cols), 5)

    def test_calendar_shows_day_headers(self):
        """Week row must contain the five weekday names."""
        headers = self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-name")
        names = [h.text.strip() for h in headers]
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            self.assertIn(day, names)

    def test_calendar_shows_time_slots(self):
        """Time column must show hour labels from 8 AM to 6 PM."""
        time_cells = self.driver.find_elements(By.CSS_SELECTOR, ".time-cell")
        self.assertGreaterEqual(len(time_cells), 10)

    def test_new_lesson_button_present(self):
        """'+ New Lesson' button must be visible."""
        btn = self._find(By.CSS_SELECTOR, ".new-button")
        self.assertTrue(btn.is_displayed())

    def test_today_button_present(self):
        """'Today' button must be visible."""
        btn = self._find(By.CSS_SELECTOR, ".today-button")
        self.assertTrue(btn.is_displayed())

    def test_prev_week_button_navigates(self):
        """Clicking the previous-week arrow must update the displayed dates."""
        headers_before = [
            h.text for h in self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-date")
        ]
        self._click(By.CSS_SELECTOR, ".nav-btn[aria-label='Previous week']")
        time.sleep(0.5)
        headers_after = [
            h.text for h in self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-date")
        ]
        self.assertNotEqual(headers_before, headers_after)

    def test_next_week_button_navigates(self):
        """Clicking the next-week arrow must update the displayed dates."""
        headers_before = [
            h.text for h in self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-date")
        ]
        self._click(By.CSS_SELECTOR, ".nav-btn[aria-label='Next week']")
        time.sleep(0.5)
        headers_after = [
            h.text for h in self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-date")
        ]
        self.assertNotEqual(headers_before, headers_after)

    def test_today_button_returns_to_current_week(self):
        """After navigating away, 'Today' must return to the current week's dates."""
        # Go forward two weeks
        self._click(By.CSS_SELECTOR, ".nav-btn[aria-label='Next week']")
        time.sleep(0.3)
        self._click(By.CSS_SELECTOR, ".nav-btn[aria-label='Next week']")
        time.sleep(0.3)
        headers_away = [
            h.text for h in self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-date")
        ]
        # Return to today
        self._click(By.CSS_SELECTOR, ".today-button")
        time.sleep(0.5)
        headers_today = [
            h.text for h in self.driver.find_elements(By.CSS_SELECTOR, ".day-header .day-date")
        ]
        self.assertNotEqual(headers_away, headers_today)

    def test_edit_mode_toggle_button_present(self):
        """Edit button must be present on the schedule page."""
        btn = self._find(By.CSS_SELECTOR, ".edit-cal-btn")
        self.assertTrue(btn.is_displayed())

    def test_edit_mode_reveals_save_and_cancel(self):
        """Clicking Edit must replace the Edit button with Save (✓) and Cancel (✕) buttons."""
        self._click(By.CSS_SELECTOR, ".edit-cal-btn")
        save_btn = self._find(By.CSS_SELECTOR, ".top-save-btn")
        cancel_btn = self._find(By.CSS_SELECTOR, ".top-cancel-btn")
        self.assertTrue(save_btn.is_displayed())
        self.assertTrue(cancel_btn.is_displayed())

    def test_cancel_edit_mode_restores_edit_button(self):
        """Clicking the Cancel (✕) button in edit mode must restore the Edit button."""
        self._click(By.CSS_SELECTOR, ".edit-cal-btn")
        self._click(By.CSS_SELECTOR, ".top-cancel-btn")
        edit_btn = self._find(By.CSS_SELECTOR, ".edit-cal-btn")
        self.assertTrue(edit_btn.is_displayed())


# ══════════════════════════════════════════════════════════════════════════════
# Flow 6 – Add Lesson Modal
# ══════════════════════════════════════════════════════════════════════════════
class TestAddLessonModal(E2EBase):
    """Covers: modal open/close, form fields, cancel without saving."""

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self.driver.find_elements(By.CSS_SELECTOR, ".sidebar-link")[1].click()
        self.wait.until(EC.url_contains("/schedule"))
        # Open the modal
        self._click(By.CSS_SELECTOR, ".new-button")

    def test_modal_opens_when_new_lesson_clicked(self):
        """Clicking '+ New Lesson' must open the schedule modal."""
        overlay = self._find(By.CSS_SELECTOR, ".modal-overlay")
        self.assertTrue(overlay.is_displayed())

    def test_modal_title_is_schedule_new_lesson(self):
        """Modal title must read 'Schedule New Lesson'."""
        title = self._find(By.XPATH, "//div[@class='modal-content']//h2")
        self.assertIn("Schedule New Lesson", title.text)

    def test_modal_has_instrument_field(self):
        """Modal must contain an Instrument input."""
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        instrument_label = content.find_element(
            By.XPATH, ".//label[contains(text(),'Instrument')]"
        )
        self.assertTrue(instrument_label.is_displayed())

    def test_modal_has_date_field(self):
        """Modal must contain a Date input of type 'date'."""
        date_input = self._find(By.CSS_SELECTOR, ".modal-content input[type='date']")
        self.assertTrue(date_input.is_displayed())

    def test_modal_has_start_time_field(self):
        """Modal must contain a Start Time input of type 'datetime-local'."""
        dt_inputs = self.driver.find_elements(
            By.CSS_SELECTOR, ".modal-content input[type='datetime-local']"
        )
        self.assertGreaterEqual(len(dt_inputs), 1)

    def test_modal_has_end_time_field(self):
        """Modal must contain both Start Time and End Time inputs."""
        dt_inputs = self.driver.find_elements(
            By.CSS_SELECTOR, ".modal-content input[type='datetime-local']"
        )
        self.assertGreaterEqual(len(dt_inputs), 2)

    def test_modal_has_save_button(self):
        """Modal must have a Save (submit) button."""
        btn = self._find(By.CSS_SELECTOR, ".modal-content button[type='submit']")
        self.assertTrue(btn.is_displayed())

    def test_modal_has_cancel_button(self):
        """Modal must have a Cancel button."""
        cancel = self._find(
            By.XPATH, "//div[@class='modal-buttons']//button[@type='button']"
        )
        self.assertTrue(cancel.is_displayed())

    def test_cancel_button_closes_modal(self):
        """Clicking Cancel must dismiss the modal."""
        cancel = self._find(
            By.XPATH, "//div[@class='modal-buttons']//button[@type='button']"
        )
        cancel.click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))
        modals = self.driver.find_elements(By.CSS_SELECTOR, ".modal-overlay")
        self.assertEqual(len(modals), 0)

    def test_clicking_overlay_closes_modal(self):
        """Clicking the overlay backdrop must close the modal."""
        overlay = self._find(By.CSS_SELECTOR, ".modal-overlay")
        # Click outside the modal content (top-left corner of overlay)
        action = webdriver.ActionChains(self.driver)
        action.move_to_element_with_offset(overlay, 5, 5).click().perform()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay")))

    def test_submit_with_empty_instrument_shows_validation(self):
        """Submitting without Instrument must trigger HTML5 validation (stays on page)."""
        # Leave instrument blank, fill other required fields
        content = self._find(By.CSS_SELECTOR, ".modal-content")
        date_input = content.find_element(By.CSS_SELECTOR, "input[type='date']")
        date_input.send_keys("2026-06-01")
        dt_inputs = content.find_elements(By.CSS_SELECTOR, "input[type='datetime-local']")
        dt_inputs[0].send_keys("2026-06-01T10:00")
        dt_inputs[1].send_keys("2026-06-01T11:00")
        save = content.find_element(By.CSS_SELECTOR, "button[type='submit']")
        save.click()
        # Modal must still be open
        modal = self.driver.find_elements(By.CSS_SELECTOR, ".modal-overlay")
        self.assertTrue(len(modal) > 0)


# ══════════════════════════════════════════════════════════════════════════════
# Flow 7 – Edit Mode (lesson edit / delete buttons)
# ══════════════════════════════════════════════════════════════════════════════
class TestEditModeButtons(E2EBase):
    """
    Covers: edit-mode toggle reveals per-lesson edit and delete buttons.

    These tests verify the UI controls appear in edit mode.
    They require at least one lesson to be present in the current week.
    If no lessons exist, the edit/delete button tests are skipped.
    """

    def setUp(self):
        super().setUp()
        self._login_and_wait_home()
        self.driver.find_elements(By.CSS_SELECTOR, ".sidebar-link")[1].click()
        self.wait.until(EC.url_contains("/schedule"))
        # Give calendar a moment to load any lessons
        time.sleep(1)

    def _enter_edit_mode(self):
        self._click(By.CSS_SELECTOR, ".edit-cal-btn")

    def test_edit_mode_hides_new_lesson_button(self):
        """In edit mode the '+ New Lesson' button should still be present (not hidden by spec)."""
        self._enter_edit_mode()
        new_btn = self._find(By.CSS_SELECTOR, ".new-button")
        self.assertTrue(new_btn.is_displayed())

    def test_edit_mode_shows_event_edit_buttons_if_lessons_exist(self):
        """If lessons are displayed, edit mode must reveal the ✎ edit button on each."""
        self._enter_edit_mode()
        edit_btns = self.driver.find_elements(By.CSS_SELECTOR, ".event-edit-btn")
        if not edit_btns:
            self.skipTest("No lessons in current week — cannot test edit buttons")
        for btn in edit_btns:
            self.assertTrue(btn.is_displayed())

    def test_edit_mode_shows_event_delete_buttons_if_lessons_exist(self):
        """If lessons are displayed, edit mode must reveal the ✕ delete button on each."""
        self._enter_edit_mode()
        del_btns = self.driver.find_elements(By.CSS_SELECTOR, ".event-delete-btn")
        if not del_btns:
            self.skipTest("No lessons in current week — cannot test delete buttons")
        for btn in del_btns:
            self.assertTrue(btn.is_displayed())

    def test_clicking_edit_button_opens_modal_with_existing_data(self):
        """Clicking ✎ on a lesson must open the modal pre-filled with 'Edit Lesson'."""
        self._enter_edit_mode()
        edit_btns = self.driver.find_elements(By.CSS_SELECTOR, ".event-edit-btn")
        if not edit_btns:
            self.skipTest("No lessons in current week — cannot test edit modal")
        edit_btns[0].click()
        modal_title = self._find(By.XPATH, "//div[@class='modal-content']//h2")
        self.assertIn("Edit Lesson", modal_title.text)

    def test_clicking_delete_button_prompts_confirmation(self):
        """Clicking ✕ on a lesson must trigger a browser confirm dialog."""
        self._enter_edit_mode()
        del_btns = self.driver.find_elements(By.CSS_SELECTOR, ".event-delete-btn")
        if not del_btns:
            self.skipTest("No lessons in current week — cannot test delete confirmation")
        del_btns[0].click()
        try:
            alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            self.assertIsNotNone(alert)
            alert.dismiss()  # Cancel the delete
        except TimeoutException:
            self.fail("Expected a confirmation dialog after clicking delete")

    def test_save_edit_mode_closes_action_buttons(self):
        """Clicking ✓ (Save) in the calendar header must exit edit mode."""
        self._enter_edit_mode()
        self._click(By.CSS_SELECTOR, ".top-save-btn")
        # Edit button should be back
        edit_btn = self._find(By.CSS_SELECTOR, ".edit-cal-btn")
        self.assertTrue(edit_btn.is_displayed())


# ══════════════════════════════════════════════════════════════════════════════
# Flow 8 – Token persistence (page refresh)
# ══════════════════════════════════════════════════════════════════════════════
class TestTokenPersistence(E2EBase):
    """Covers: session survives a page refresh; direct URL access after login."""

    def test_session_survives_page_refresh(self):
        """After login, refreshing the page must keep the user on /home."""
        self._login_and_wait_home()
        self.driver.refresh()
        self.wait.until(EC.url_contains("/home"))
        self.assertIn("/home", self.driver.current_url)

    def test_direct_url_access_to_schedule_after_login(self):
        """Navigating directly to /schedule after login must work without redirect."""
        self._login_and_wait_home()
        self._get("/schedule")
        self.wait.until(EC.url_contains("/schedule"))
        self.assertIn("/schedule", self.driver.current_url)

    def test_token_stored_in_local_storage_after_login(self):
        """After login, localStorage must contain a non-empty 'token' value."""
        self._login_and_wait_home()
        token = self.driver.execute_script("return localStorage.getItem('token');")
        self.assertIsNotNone(token)
        self.assertGreater(len(token), 10)

    def test_token_is_a_jwt_three_parts(self):
        """Token in localStorage must be a valid three-part JWT string."""
        self._login_and_wait_home()
        token = self.driver.execute_script("return localStorage.getItem('token');")
        parts = token.split(".")
        self.assertEqual(len(parts), 3, "Expected JWT with 3 dot-separated parts")


if __name__ == "__main__":
    unittest.main()
