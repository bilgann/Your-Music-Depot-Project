"""
Shared config, driver factory, and base test class for all e2e Selenium tests.

Chrome opens ONCE per test class (setUpClass / tearDownClass) and is reused
across every test method in that class.  Before each test, setUp navigates to
/home, re-logging-in automatically if the session was lost (e.g. after a
logout test).  This eliminates the browser-restart overhead that was previously
paid on every single test method.

Test classes that require an unauthenticated state (login page, auth-guard
tests) should override setUp and call self._clear_session() instead of
super().setUp().

Environment variables (optional)
---------------------------------
    E2E_BASE_URL  – override default frontend URL   (default: http://localhost:3000)
    E2E_USERNAME  – valid login username             (default: barnes)
    E2E_PASSWORD  – valid login password             (default: password)
    E2E_HEADLESS  – set to "1" to run headless       (default: 0)
"""

import os
import unittest

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

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

# Secondary display offset — set E2E_DISPLAY_X / E2E_DISPLAY_Y to override.
# Default assumes the secondary monitor sits to the right of a 1920-wide primary.
DISPLAY_X = int(os.getenv("E2E_DISPLAY_X", "1920"))
DISPLAY_Y = int(os.getenv("E2E_DISPLAY_Y", "0"))

DEFAULT_TIMEOUT = 10  # seconds


# ── Driver factory ─────────────────────────────────────────────────────────────
def _make_driver() -> webdriver.Chrome:
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # Position the window on the secondary display before maximising.
    opts.add_argument(f"--window-position={DISPLAY_X},{DISPLAY_Y}")
    opts.add_argument("--start-maximized")

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    }
    opts.add_experimental_option("prefs", prefs)

    try:
        from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
    except Exception:
        driver = webdriver.Chrome(options=opts)

    # Ensure the window is maximised on whichever screen it landed on.
    driver.maximize_window()
    return driver


# ── Base class ─────────────────────────────────────────────────────────────────
class E2EBase(unittest.TestCase):
    """
    Base class for all e2e Selenium tests.

    One Chrome window is shared across every test method in a class.
    setUp navigates to /home before each test, automatically re-authenticating
    if the session was cleared (e.g. by a preceding logout test).
    """

    driver: webdriver.Chrome
    wait: WebDriverWait

    # ── Class lifecycle (one browser per class) ────────────────────────────────

    @classmethod
    def setUpClass(cls):
        cls.driver = _make_driver()
        cls.wait = WebDriverWait(cls.driver, DEFAULT_TIMEOUT)
        cls._class_login()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    @classmethod
    def _class_login(cls):
        """Log in once when the class is set up."""
        cls.driver.get(BASE_URL + "/login")
        cls.wait.until(EC.presence_of_element_located((By.ID, "username")))
        cls.driver.find_element(By.ID, "username").send_keys(USERNAME)
        cls.driver.find_element(By.ID, "password").send_keys(PASSWORD)
        cls.driver.find_element(By.CSS_SELECTOR, ".login-submit").click()
        cls.wait.until(EC.url_contains("/home"))

    # ── Instance lifecycle (reset navigation per test, share browser) ──────────

    def setUp(self):
        """
        Navigate to /home before each test.
        Re-authenticates automatically if the session was lost.
        """
        self._dismiss_alert_if_present()
        self._ensure_home()

    def tearDown(self):
        """Dismiss any lingering alerts so they don't bleed into the next test."""
        self._dismiss_alert_if_present()

    # ── Core helpers ───────────────────────────────────────────────────────────

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

    # ── Auth helpers ───────────────────────────────────────────────────────────

    def _ensure_home(self):
        """
        Navigate to /home.  If the app redirects to /login the session has
        expired — fill in the credentials and continue.
        """
        self.driver.get(BASE_URL + "/home")
        try:
            self.wait.until(
                lambda d: "/home" in d.current_url or "/login" in d.current_url
            )
        except TimeoutException:
            pass
        if "/login" in self.driver.current_url:
            self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            self.driver.find_element(By.ID, "username").send_keys(USERNAME)
            self.driver.find_element(By.ID, "password").send_keys(PASSWORD)
            self.driver.find_element(By.CSS_SELECTOR, ".login-submit").click()
            self.wait.until(EC.url_contains("/home"))

    def _do_login(self, username: str = USERNAME, password: str = PASSWORD):
        """Navigate to /login and submit credentials."""
        self._get("/login")
        self._type(By.ID, "username", username)
        self._type(By.ID, "password", password)
        self._click(By.CSS_SELECTOR, ".login-submit")

    def _login_and_wait_home(self):
        """
        Ensure the browser is on /home (logged in).

        Since setUp already handles this, this is typically a no-op.
        Kept for backward compatibility with existing test classes.
        """
        if "/home" not in self.driver.current_url:
            self._ensure_home()

    def _clear_session(self):
        """
        Remove the auth token from localStorage and navigate to /login.

        Use this in setUp overrides for test classes that need an
        unauthenticated browser state (e.g. login-page tests, auth-guard tests).
        """
        try:
            self.driver.execute_script("localStorage.removeItem('token');")
        except Exception:
            pass
        self._get("/login")

    # ── Alert helpers ──────────────────────────────────────────────────────────

    def _dismiss_alert_if_present(self):
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except (NoAlertPresentException, Exception):
            pass
