"""
Unit tests covering:
  FR-15 — Conflict Alert: scheduling conflicts surface as ConflictError → 409
  FR-16 — Data Validation: required fields and type checks on all resources
  FR-17 — Referential Integrity: FK violations mapped to ConflictError → 409
"""
import unittest

from flask import Flask

from backend.app.domain.exceptions.exceptions import ConflictError, NotFoundError, ValidationError
from backend.app.api.contracts.validation import error_response, parse_db_error, validate

_app = Flask(__name__)


# ── Instructor ────────────────────────────────────────────────────────────────

class TestValidateInstructor(unittest.TestCase):
    """FR-16: Instructor schema — name is required; email/phone must be str."""

    def test_missing_name_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            validate({}, "instructor")
        self.assertIn("name", [e["field"] for e in ctx.exception.errors])

    def test_empty_name_raises(self):
        with self.assertRaises(ValidationError):
            validate({"name": ""}, "instructor")

    def test_valid_minimal_payload_passes(self):
        validate({"name": "Alice Smith"}, "instructor")

    def test_email_must_be_str(self):
        with self.assertRaises(ValidationError):
            validate({"name": "Alice", "email": 99}, "instructor")

    def test_phone_must_be_str(self):
        with self.assertRaises(ValidationError):
            validate({"name": "Alice", "phone": 1234567890}, "instructor")


# ── Student ───────────────────────────────────────────────────────────────────

class TestValidateStudent(unittest.TestCase):
    """FR-16: Student schema — name or person_id is required (validated at service level)."""

    def test_missing_name_and_person_id_raises(self):
        """Service raises ValidationError when neither name nor person_id is supplied."""
        from unittest.mock import MagicMock
        from backend.app.infrastructure.database.database import DatabaseConnection
        DatabaseConnection._instance = MagicMock()
        from backend.app.application.services import create_student
        with self.assertRaises(ValidationError) as ctx:
            create_student({})
        self.assertIn("name", [e["field"] for e in ctx.exception.errors])

    def test_empty_name_without_person_id_raises(self):
        """Service raises ValidationError when name is empty and person_id is absent."""
        from unittest.mock import MagicMock
        from backend.app.infrastructure.database.database import DatabaseConnection
        DatabaseConnection._instance = MagicMock()
        from backend.app.application.services import create_student
        with self.assertRaises(ValidationError):
            create_student({"name": ""})

    def test_valid_student_passes(self):
        validate({"name": "Bob Jones", "email": "bob@example.com"}, "student")

    def test_email_must_be_str(self):
        with self.assertRaises(ValidationError):
            validate({"name": "Bob", "email": 123}, "student")


# ── Room ──────────────────────────────────────────────────────────────────────

class TestValidateRoom(unittest.TestCase):
    """FR-16: Room schema — name required; capacity must be int."""

    def test_missing_name_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            validate({}, "room")
        self.assertIn("name", [e["field"] for e in ctx.exception.errors])

    def test_capacity_must_be_int(self):
        with self.assertRaises(ValidationError):
            validate({"name": "Room A", "capacity": "large"}, "room")

    def test_valid_room_passes(self):
        validate({"name": "Room A", "capacity": 5}, "room")


# ── Lesson ────────────────────────────────────────────────────────────────────

class TestValidateLesson(unittest.TestCase):
    """FR-16: Lesson schema — 5 required fields; rate must be numeric."""

    _VALID = {
        "student_id": "s1", "instructor_id": "i1", "room_id": "r1",
        "start_time": "2025-01-01T10:00", "end_time": "2025-01-01T11:00",
    }

    def test_empty_body_flags_all_required_fields(self):
        with self.assertRaises(ValidationError) as ctx:
            validate({}, "lesson")
        fields = [e["field"] for e in ctx.exception.errors]
        for f in ("instructor_id", "room_id", "start_time", "end_time"):
            self.assertIn(f, fields)

    def test_rate_rejects_string(self):
        with self.assertRaises(ValidationError):
            validate({**self._VALID, "rate": "fifty"}, "lesson")

    def test_rate_accepts_int(self):
        validate({**self._VALID, "rate": 50}, "lesson")

    def test_rate_accepts_float(self):
        validate({**self._VALID, "rate": 50.0}, "lesson")

    def test_start_time_must_be_str(self):
        with self.assertRaises(ValidationError):
            validate({**self._VALID, "start_time": 20250101}, "lesson")


# ── Invoice ───────────────────────────────────────────────────────────────────

class TestValidateInvoice(unittest.TestCase):
    """FR-16: Invoice schema — student_id and total_amount required."""

    def test_missing_required_fields_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            validate({}, "invoice")
        fields = [e["field"] for e in ctx.exception.errors]
        self.assertIn("student_id", fields)
        self.assertIn("total_amount", fields)

    def test_total_amount_must_be_numeric(self):
        with self.assertRaises(ValidationError):
            validate({"student_id": "s1", "total_amount": "one hundred"}, "invoice")

    def test_valid_invoice_passes(self):
        validate({"student_id": "s1", "total_amount": 150.0}, "invoice")


# ── Payment ───────────────────────────────────────────────────────────────────

class TestValidatePayment(unittest.TestCase):
    """FR-16: Payment schema — invoice_id and amount required."""

    def test_missing_required_fields_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            validate({}, "payment")
        fields = [e["field"] for e in ctx.exception.errors]
        self.assertIn("invoice_id", fields)
        self.assertIn("amount", fields)

    def test_amount_must_be_numeric(self):
        with self.assertRaises(ValidationError):
            validate({"invoice_id": "inv-1", "amount": "fifty"}, "payment")


# ── Partial (PUT) validation ──────────────────────────────────────────────────

class TestPartialValidation(unittest.TestCase):
    """FR-16: PUT validation skips required fields but still type-checks."""

    def test_partial_skips_required_check(self):
        validate({"email": "new@example.com"}, "student", partial=True)

    def test_partial_still_enforces_types(self):
        with self.assertRaises(ValidationError):
            validate({"capacity": "ten"}, "room", partial=True)

    def test_none_body_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            validate(None, "student", partial=True)
        self.assertEqual(ctx.exception.errors[0]["field"], "_body")


# ── DB error mapping ──────────────────────────────────────────────────────────

class TestParseDbError(unittest.TestCase):
    """FR-15, FR-17: PostgreSQL error codes map to typed application common."""

    def test_fk_violation_code_maps_to_conflict(self):
        self.assertIsInstance(parse_db_error(Exception("ERROR: 23503 foreign key")), ConflictError)

    def test_fk_keyword_maps_to_conflict(self):
        self.assertIsInstance(parse_db_error(Exception("foreign key constraint violated")), ConflictError)

    def test_unique_violation_code_maps_to_conflict(self):
        self.assertIsInstance(parse_db_error(Exception("ERROR: 23505 unique")), ConflictError)

    def test_duplicate_keyword_maps_to_conflict(self):
        self.assertIsInstance(parse_db_error(Exception("duplicate key value")), ConflictError)

    def test_not_null_violation_maps_to_validation_error(self):
        self.assertIsInstance(parse_db_error(Exception("ERROR: 23502 not-null constraint")), ValidationError)

    def test_unknown_exception_returned_unchanged(self):
        exc = RuntimeError("unrelated")
        self.assertIs(parse_db_error(exc), exc)


# ── HTTP error responses ──────────────────────────────────────────────────────

class TestErrorResponse(unittest.TestCase):
    """FR-15, FR-16, FR-17: error_response() produces correct HTTP status codes."""

    def setUp(self):
        self._ctx = _app.app_context()
        self._ctx.push()

    def tearDown(self):
        self._ctx.pop()

    def test_validation_error_returns_422(self):
        _, status = error_response(ValidationError([{"field": "name", "message": "required."}]))
        self.assertEqual(status, 422)

    def test_not_found_error_returns_404(self):
        _, status = error_response(NotFoundError("Not found."))
        self.assertEqual(status, 404)

    def test_conflict_error_returns_409(self):
        """FR-15, FR-17: Any conflict (double-booking or FK violation) → 409."""
        _, status = error_response(ConflictError("Booking conflict detected."))
        self.assertEqual(status, 409)

    def test_generic_exception_returns_500(self):
        _, status = error_response(RuntimeError("unexpected"))
        self.assertEqual(status, 500)

    def test_conflict_response_body_has_message(self):
        """FR-15: The 409 body communicates the conflict to the caller."""
        response, _ = error_response(ConflictError("Instructor already booked."))
        body = response.get_json()
        self.assertFalse(body["success"])
        self.assertIsNotNone(body.get("message"))

    def test_raw_fk_exception_ultimately_returns_409(self):
        """FR-17: Raw DB FK error is mapped through to a 409."""
        _, status = error_response(Exception("ERROR: 23503 foreign key violation"))
        self.assertEqual(status, 409)

    def test_validation_error_response_includes_field_errors(self):
        """FR-16: 422 body includes per-field error details."""
        errors = [{"field": "name", "message": "name is required."}]
        response, _ = error_response(ValidationError(errors))
        body = response.get_json()
        self.assertIn("errors", body)
        self.assertEqual(body["errors"][0]["field"], "name")


if __name__ == "__main__":
    unittest.main()