"""
Shared config, driver factory, and base test class for all e2e Selenium tests.

Environment variables (optional)
---------------------------------
    E2E_BASE_URL  – override default frontend URL   (default: http://localhost:3000)
    E2E_USERNAME  – valid login username             (default: barnes)
    E2E_PASSWORD  – valid login password             (default: password)
    E2E_HEADLESS  – set to "1" to run headless       (default: 0)
"""

import os
import unittest

from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
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

    try:
        from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=opts)
    except Exception:
        return webdriver.Chrome(options=opts)


# ── Base class ─────────────────────────────────────────────────────────────────
class E2EBase(unittest.TestCase):
    """Base class – creates a fresh browser for every test."""

    driver: webdriver.Chrome
    wait: WebDriverWait

    def setUp(self):
        self.driver = _make_driver()
        self.wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT)

    def tearDown(self):
        self.driver.quit()

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
