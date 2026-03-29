"""
Integration and structural tests covering:
  NFR-01 — Technical Environment: CORS headers present for browser access
  NFR-02 — System Integration: standardized JSON response envelope
  NFR-03 — Portability: no OS-specific dependencies
  NFR-04 — Maintainability: domain-based folder structure present
  NFR-05 — Speed: API responses complete within 3 seconds
  NFR-06 — Capacity: handles 200 students / 20 instructors without error
  NFR-07 — Availability: app initialises and serves requests
  NFR-11 — Privacy Compliance: retention fields present on financial records
  NFR-12 — Data Export: CSV export endpoints (not yet implemented — skipped)
"""
import os
import time
import unittest
from unittest.mock import MagicMock, patch

from backend.app.application.singletons import Auth
from backend.app.application.singletons.database import DatabaseConnection

_BACKEND_ROOT = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)


def _build():
    DatabaseConnection._instance = MagicMock()
    Auth._instance = None
    from backend import build_app
    app = build_app()
    app.config["TESTING"] = True
    return app.test_client()


_client = _build()
_token = _client.post("/user/login?username=barnes&password=password").get_json()["data"]
_H = {"Authorization": f"Bearer {_token}"}


# ── NFR-01: Browser / CORS ────────────────────────────────────────────────────

class TestNFRTechnicalEnvironment(unittest.TestCase):
    """NFR-01: Web app accessible via modern browsers — CORS headers present."""

    def test_cors_header_present_on_api_response(self):
        """NFR-01: CORS header is sent when Origin matches the allowed frontend."""
        with patch("backend.app.services.student.list_students", return_value=([], 0)):
            res = _client.get(
                "/api/students",
                headers={"Origin": "http://localhost:3000"},
            )
        self.assertIn("Access-Control-Allow-Origin", res.headers)

    def test_options_preflight_does_not_error(self):
        """NFR-01: Browser CORS preflight (OPTIONS) is handled without a 5xx error."""
        res = _client.options(
            "/api/students",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertNotIn(res.status_code, (500, 501, 502, 503))

    def test_all_api_responses_use_json_content_type(self):
        """NFR-01, NFR-02: API responses carry application/json."""
        with patch("backend.app.services.student.list_students", return_value=([], 0)):
            res = _client.get("/api/students")
        self.assertIn("application/json", res.content_type)


# ── NFR-02: API contract ──────────────────────────────────────────────────────

class TestNFRSystemIntegration(unittest.TestCase):
    """NFR-02: Flask REST API returns a standardized {success, message, data} envelope."""

    def test_success_response_has_required_keys(self):
        with patch("backend.app.services.student.list_students", return_value=([], 0)):
            res = _client.get("/api/students", headers=_H)
        body = res.get_json()
        for key in ("success", "message", "data"):
            self.assertIn(key, body)
        self.assertTrue(body["success"])

    def test_error_response_has_required_keys(self):
        with patch("backend.app.services.student.get_student_by_id", return_value=[]):
            res = _client.get("/api/students/nonexistent")
        body = res.get_json()
        self.assertIn("success", body)
        self.assertIn("message", body)
        self.assertFalse(body["success"])

    def test_unknown_endpoint_returns_json_404(self):
        """NFR-02: Unknown routes return JSON, not an HTML error page."""
        res = _client.get("/api/this-route-does-not-exist")
        self.assertEqual(res.status_code, 404)
        body = res.get_json()
        self.assertIsNotNone(body)
        self.assertFalse(body["success"])

    def test_wrong_http_method_returns_json_405(self):
        """NFR-02: Wrong method returns JSON 405, not an HTML page."""
        res = _client.patch("/api/students")
        self.assertEqual(res.status_code, 405)
        self.assertIsNotNone(res.get_json())

    def test_validation_error_includes_field_errors_array(self):
        """NFR-02: 422 validation responses include per-field errors for the frontend."""
        res = _client.post("/api/students", json={}, headers=_H)
        body = res.get_json()
        self.assertEqual(res.status_code, 422)
        self.assertIn("errors", body)
        self.assertIsInstance(body["errors"], list)


# ── NFR-03: Portability ───────────────────────────────────────────────────────

class TestNFRPortability(unittest.TestCase):
    """NFR-03: System runs on Windows, macOS, and Linux without OS-specific deps."""

    def test_requirements_contain_no_windows_only_packages(self):
        """NFR-03: requirements.txt must not list Windows-exclusive packages."""
        req_path = os.path.join(_BACKEND_ROOT, "requirements.txt")
        windows_only = {"pywin32", "winreg", "win32api", "win32con", "comtypes"}
        with open(req_path, encoding="utf-8") as fh:
            packages = {
                line.strip().split("==")[0].split(">=")[0].lower()
                for line in fh
                if line.strip() and not line.startswith("#")
            }
        overlap = packages & windows_only
        self.assertEqual(overlap, set(), msg=f"Windows-only packages detected: {overlap}")

    def test_database_singleton_uses_os_path_for_paths(self):
        """NFR-03: DatabaseConnection constructs paths with os.path (cross-platform)."""
        db_path = os.path.join(_BACKEND_ROOT, "app", "singletons", "database.py")
        with open(db_path, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("os.path", content)

    def test_no_backslash_path_literals_in_app_source(self):
        """NFR-03: Source files under app/ must not hard-code Windows backslash paths."""
        import re
        app_dir = os.path.join(_BACKEND_ROOT, "app")
        violations = []
        for root, dirs, files in os.walk(app_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                fpath = os.path.join(root, fname)
                with open(fpath, encoding="utf-8") as fh:
                    content = fh.read()
                # Flag string literals that contain backslash-separated path segments
                # (e.g., "C:\\Users\\...") but ignore escaped characters like \n, \t
                if re.search(r'["\'][A-Za-z]:\\\\', content):
                    violations.append(os.path.relpath(fpath, _BACKEND_ROOT))
        self.assertEqual(violations, [], msg=f"Hard-coded Windows paths in: {violations}")


# ── NFR-04: Maintainability ───────────────────────────────────────────────────

class TestNFRMaintainability(unittest.TestCase):
    """NFR-04: Domain-based folder structure; separate service/controller per entity."""

    def _exists(self, *parts):
        return os.path.exists(os.path.join(_BACKEND_ROOT, *parts))

    def test_domain_directories_exist(self):
        """NFR-04: Expected domain layer directories are present."""
        for folder in ("app/controllers", "app/services", "app/models",
                       "app/dtos", "app/singletons", "app/domain"):
            self.assertTrue(
                self._exists(*folder.split("/")),
                msg=f"Missing domain directory: {folder}",
            )

    def test_test_layer_directories_exist(self):
        """NFR-04: Test layers (unit, integration, component) are separated."""
        for folder in ("tests/unit", "tests/integration", "tests/component"):
            self.assertTrue(
                self._exists(*folder.split("/")),
                msg=f"Missing test layer directory: {folder}",
            )

    def test_service_module_per_resource(self):
        """NFR-04: Each business entity has a dedicated service module."""
        for svc in ("student", "instructor", "room", "lesson", "invoice", "payment"):
            self.assertTrue(
                self._exists("app", "services", f"{svc}.py"),
                msg=f"Service module missing: {svc}.py",
            )

    def test_controller_module_per_resource(self):
        """NFR-04: Each business entity has a dedicated controller module."""
        for ctrl in ("student", "instructor", "room", "lesson", "invoice", "payment", "user"):
            self.assertTrue(
                self._exists("app", "controllers", f"{ctrl}.py"),
                msg=f"Controller module missing: {ctrl}.py",
            )

    def test_contracts_module_exists(self):
        """NFR-04: Shared validation/error dtos are encapsulated in one module."""
        for mod in ("validation.py", "errors.py", "response.py"):
            self.assertTrue(self._exists("app", "dtos", mod))

    def test_singleton_modules_exist(self):
        """NFR-04: Shared services (DB, Auth) are singletons in their own module."""
        for mod in ("database.py", "auth.py"):
            self.assertTrue(self._exists("app", "singletons", mod))


# ── NFR-05 / NFR-07: Performance and Availability ────────────────────────────

class TestNFRPerformanceAndAvailability(unittest.TestCase):
    """
    NFR-05: Responses complete within 3 seconds under normal usage.
    NFR-07: Application is available and serves requests.

    Note: timings here measure Flask routing + serialisation overhead only.
    Full performance validation requires a staging environment with live Supabase.
    """

    _THRESHOLD = 3.0  # seconds (NFR-05)

    def _timed(self, method, path, **kwargs):
        t0 = time.perf_counter()
        res = getattr(_client, method)(path, **kwargs)
        return res, time.perf_counter() - t0

    def test_list_students_within_threshold(self):
        with patch("backend.app.services.student.list_students", return_value=([], 0)):
            _, elapsed = self._timed("get", "/api/students")
        self.assertLess(elapsed, self._THRESHOLD)

    def test_list_instructors_within_threshold(self):
        with patch("backend.app.services.instructor.list_instructors", return_value=([], 0)):
            _, elapsed = self._timed("get", "/api/instructors")
        self.assertLess(elapsed, self._THRESHOLD)

    def test_list_lessons_within_threshold(self):
        with patch("backend.app.services.lesson.get_all_lessons", return_value=[]):
            _, elapsed = self._timed("get", "/api/lessons")
        self.assertLess(elapsed, self._THRESHOLD)

    def test_list_invoices_within_threshold(self):
        with patch("backend.app.services.invoice.get_all_invoices", return_value=[]):
            _, elapsed = self._timed("get", "/api/invoices")
        self.assertLess(elapsed, self._THRESHOLD)

    def test_app_is_available_and_responds(self):
        """NFR-07: Application initialises and serves at least one endpoint."""
        with patch("backend.app.services.student.list_students", return_value=([], 0)):
            res = _client.get("/api/students", headers=_H)
        self.assertIn(res.status_code, (200, 201, 204))

    def test_unknown_route_does_not_crash_app(self):
        """NFR-07: App remains available even for unknown routes."""
        res = _client.get("/api/nonexistent-health-check")
        self.assertIsNotNone(res.get_json())
        self.assertNotIn(res.status_code, (500, 502, 503))


# ── NFR-06: Capacity ──────────────────────────────────────────────────────────

class TestNFRCapacity(unittest.TestCase):
    """NFR-06: System supports 200 active students and 20 instructors without degradation."""

    _THRESHOLD = 3.0

    def test_200_student_records_returned_without_error(self):
        dataset = [
            {"student_id": f"s{i}", "name": f"Student {i}", "email": f"s{i}@test.com"}
            for i in range(200)
        ]
        with patch("backend.app.services.student.list_students", return_value=(dataset, 200)):
            t0 = time.perf_counter()
            res = _client.get("/api/students", headers=_H)
            elapsed = time.perf_counter() - t0
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.get_json()["data"]), 200)
        self.assertLess(elapsed, self._THRESHOLD)

    def test_20_instructor_records_returned_without_error(self):
        dataset = [
            {"instructor_id": f"i{i}", "name": f"Instructor {i}"}
            for i in range(20)
        ]
        with patch("backend.app.services.instructor.list_instructors", return_value=(dataset, 20)):
            res = _client.get("/api/instructors", headers=_H)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.get_json()["data"]), 20)

    def test_large_lesson_list_serialises_correctly(self):
        """NFR-06: 5 years × ~40 weeks × 4 lessons/week = ~800 lessons handled."""
        dataset = [
            {
                "lesson_id": f"l{i}",
                "student_id": f"s{i % 200}",
                "instructor_id": f"i{i % 20}",
                "start_time": "2025-09-10T10:00:00",
                "rate": 50.0,
            }
            for i in range(800)
        ]
        with patch("backend.app.services.lesson.get_all_lessons", return_value=dataset):
            t0 = time.perf_counter()
            res = _client.get("/api/lessons", headers=_H)
            elapsed = time.perf_counter() - t0
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.get_json()["data"]), 800)
        self.assertLess(elapsed, self._THRESHOLD)


# ── NFR-11: Privacy Compliance ────────────────────────────────────────────────

class TestNFRPrivacyCompliance(unittest.TestCase):
    """
    NFR-11: PIPEDA compliance; financial records retained for a minimum of 7 years.
    These tests verify that the data model exposes the fields needed for retention audits.
    """

    def test_invoice_record_includes_period_dates(self):
        """NFR-11: Invoice records expose period_start / period_end for retention tracking."""
        invoice = {
            "invoice_id": "inv-1", "student_id": "s1",
            "period_start": "2025-01-01", "period_end": "2025-01-31",
            "total_amount": 100.0, "amount_paid": 0.0, "status": "Pending",
        }
        with patch("backend.app.services.invoice.get_invoice_by_id", return_value=[invoice]):
            res = _client.get("/api/invoices/inv-1", headers=_H)
        record = res.get_json()["data"]
        self.assertIn("period_start", record, "period_start required for 7-year retention")
        self.assertIn("period_end", record, "period_end required for 7-year retention")

    def test_payment_record_includes_paid_on_date(self):
        """NFR-11: Payment records expose paid_on for audit / financial record retention."""
        payment = {
            "payment_id": "p1", "invoice_id": "inv-1",
            "amount": 50.0, "paid_on": "2025-01-15",
        }
        with patch("backend.app.services.payment.get_payment_by_id", return_value=[payment]):
            res = _client.get("/api/payments/p1", headers=_H)
        record = res.get_json()["data"]
        self.assertIn("paid_on", record, "paid_on field required for financial record retention")

    def test_invoice_includes_total_and_paid_amounts(self):
        """NFR-11: Financial totals are preserved for audit purposes."""
        invoice = {
            "invoice_id": "inv-1", "student_id": "s1",
            "total_amount": 200.0, "amount_paid": 50.0, "status": "Pending",
        }
        with patch("backend.app.services.invoice.get_invoice_by_id", return_value=[invoice]):
            res = _client.get("/api/invoices/inv-1", headers=_H)
        record = res.get_json()["data"]
        self.assertIn("total_amount", record)
        self.assertIn("amount_paid", record)


# ── NFR-12: Data Export (not yet implemented) ─────────────────────────────────

class TestNFRDataExport(unittest.TestCase):
    """
    NFR-12: System must allow exporting student lists, schedules, and financial
    data to CSV for backup or ownership transfer.

    These tests are skipped because no export endpoints exist yet.
    Expected endpoints (to be implemented):
      GET /api/students/export?format=csv
      GET /api/lessons/export?format=csv
      GET /api/invoices/export?format=csv
    """

    @unittest.skip("NFR-12 not yet implemented: no CSV export endpoint for students")
    def test_student_list_export_returns_csv(self):
        res = _client.get("/api/students/export?format=csv")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.content_type)

    @unittest.skip("NFR-12 not yet implemented: no CSV export endpoint for lessons")
    def test_schedule_export_returns_csv(self):
        res = _client.get("/api/lessons/export?format=csv")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.content_type)

    @unittest.skip("NFR-12 not yet implemented: no CSV export endpoint for invoices")
    def test_financial_export_returns_csv(self):
        res = _client.get("/api/invoices/export?format=csv")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.content_type)

    @unittest.skip("NFR-12 not yet implemented: no CSV export endpoint for payments")
    def test_payment_export_returns_csv(self):
        res = _client.get("/api/payments/export?format=csv")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.content_type)


if __name__ == "__main__":
    unittest.main()