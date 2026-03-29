"""
Unit tests for the domain layer.

All functions tested here are pure (no DB, no HTTP, no framework deps).
Each test module covers one domain file:

  domain/attendance.py  — VALID_CHARGE_TYPES, validate_policy_data()
  domain/invoice.py     — attendance_label(), apply_policy_rule(),
                          calculate_lesson_charge(), build_line_items(),
                          compute_outstanding_balance()
  domain/payment.py     — validate_payment_request(), compute_apply_amount(),
                          determine_invoice_status()
  domain/scheduling.py  — validate_no_instructor_conflict(),
                          validate_no_room_conflict()
  domain/person.py      — prepare_person_linked_create(),
                          extract_person_update_fields()
"""
import unittest

from backend.app.common.base import ValidationError
from backend.app.common.payment import (
    InvoiceAlreadyPaidError,
    InvoiceCancelledError,
    OverpaymentError,
)
from backend.app.common.scheduling import InstructorUnavailableError, RoomUnavailableError


# ── domain/attendance.py ──────────────────────────────────────────────────────

class TestAttendanceDomain(unittest.TestCase):
    """domain/attendance — charge type constants and policy data validation."""

    def test_valid_charge_types_contains_expected_values(self):
        from backend.app.domain.attendance import VALID_CHARGE_TYPES
        self.assertIn("none", VALID_CHARGE_TYPES)
        self.assertIn("flat", VALID_CHARGE_TYPES)
        self.assertIn("percentage", VALID_CHARGE_TYPES)

    def test_validate_policy_data_passes_for_valid_types(self):
        from backend.app.domain.attendance import validate_policy_data
        validate_policy_data({
            "absent_charge_type": "flat",
            "cancel_charge_type": "percentage",
            "late_cancel_charge_type": "none",
        })  # should not raise

    def test_validate_policy_data_rejects_invalid_type(self):
        from backend.app.domain.attendance import validate_policy_data
        with self.assertRaises(ValidationError) as ctx:
            validate_policy_data({"absent_charge_type": "weekly"})
        fields = [e["field"] for e in ctx.exception.errors]
        self.assertIn("absent_charge_type", fields)

    def test_validate_policy_data_collects_multiple_errors(self):
        from backend.app.domain.attendance import validate_policy_data
        with self.assertRaises(ValidationError) as ctx:
            validate_policy_data({
                "absent_charge_type": "bad",
                "late_cancel_charge_type": "also_bad",
            })
        fields = [e["field"] for e in ctx.exception.errors]
        self.assertIn("absent_charge_type", fields)
        self.assertIn("late_cancel_charge_type", fields)

    def test_validate_policy_data_ignores_unknown_keys(self):
        from backend.app.domain.attendance import validate_policy_data
        # Extra keys not in the schema are silently ignored
        validate_policy_data({"name": "My Policy", "is_default": False})

    def test_validate_policy_data_partial_allows_missing_keys(self):
        from backend.app.domain.attendance import validate_policy_data
        # partial=True — only validate keys that are present
        validate_policy_data({"absent_charge_type": "flat"}, partial=True)


# ── domain/invoice.py ─────────────────────────────────────────────────────────

class TestInvoiceDomainLabels(unittest.TestCase):
    """domain/invoice — attendance_label()"""

    def test_present_maps_to_present(self):
        from backend.app.domain.invoice import attendance_label
        self.assertEqual(attendance_label("Present"), "Present")

    def test_absent_maps_to_absent(self):
        from backend.app.domain.invoice import attendance_label
        self.assertEqual(attendance_label("Absent"), "Absent")

    def test_late_cancel_maps_to_late_cancellation(self):
        from backend.app.domain.invoice import attendance_label
        self.assertEqual(attendance_label("Late Cancel"), "Late cancellation")

    def test_excused_maps_to_excused(self):
        from backend.app.domain.invoice import attendance_label
        self.assertEqual(attendance_label("Excused"), "Excused")

    def test_none_maps_to_attended(self):
        from backend.app.domain.invoice import attendance_label
        self.assertEqual(attendance_label(None), "Attended")

    def test_unknown_status_returned_as_is(self):
        from backend.app.domain.invoice import attendance_label
        self.assertEqual(attendance_label("SomeNewStatus"), "SomeNewStatus")


class TestInvoiceDomainPolicyRule(unittest.TestCase):
    """domain/invoice — apply_policy_rule()"""

    def test_none_type_returns_zero(self):
        from backend.app.domain.invoice import apply_policy_rule
        self.assertEqual(apply_policy_rule(100.0, "none", 50), 0.0)

    def test_flat_type_returns_flat_amount(self):
        from backend.app.domain.invoice import apply_policy_rule
        self.assertAlmostEqual(apply_policy_rule(100.0, "flat", 25.0), 25.0)

    def test_percentage_type_calculates_correctly(self):
        from backend.app.domain.invoice import apply_policy_rule
        self.assertAlmostEqual(apply_policy_rule(80.0, "percentage", 50), 40.0)

    def test_percentage_rounds_to_two_decimals(self):
        from backend.app.domain.invoice import apply_policy_rule
        # 33.33% of 100 = 33.33
        result = apply_policy_rule(100.0, "percentage", 33.33)
        self.assertAlmostEqual(result, 33.33, places=2)

    def test_flat_ignores_rate(self):
        from backend.app.domain.invoice import apply_policy_rule
        self.assertEqual(apply_policy_rule(999.0, "flat", 10.0), 10.0)


class TestInvoiceDomainChargeCalculation(unittest.TestCase):
    """domain/invoice — calculate_lesson_charge()"""

    _POLICY = {
        "absent_charge_type": "flat", "absent_charge_value": 20,
        "cancel_charge_type": "none", "cancel_charge_value": 0,
        "late_cancel_charge_type": "percentage", "late_cancel_charge_value": 50,
    }

    def _lesson(self, rate=60.0, status=None):
        return {"lesson_id": "l1", "start_time": "2025-01-10T10:00:00",
                "rate": rate, "attendance_status": status}

    def test_present_charges_full_rate(self):
        from backend.app.domain.invoice import calculate_lesson_charge
        self.assertAlmostEqual(calculate_lesson_charge(self._lesson(60.0, "Present"), None), 60.0)

    def test_null_status_charges_full_rate(self):
        from backend.app.domain.invoice import calculate_lesson_charge
        self.assertAlmostEqual(calculate_lesson_charge(self._lesson(60.0, None), None), 60.0)

    def test_excused_charges_zero(self):
        from backend.app.domain.invoice import calculate_lesson_charge
        self.assertEqual(calculate_lesson_charge(self._lesson(60.0, "Excused"), None), 0.0)

    def test_absent_applies_flat_policy_charge(self):
        from backend.app.domain.invoice import calculate_lesson_charge
        # Absent → flat $20 per policy
        self.assertAlmostEqual(
            calculate_lesson_charge(self._lesson(60.0, "Absent"), self._POLICY), 20.0
        )

    def test_late_cancel_applies_percentage_policy_charge(self):
        from backend.app.domain.invoice import calculate_lesson_charge
        # Late Cancel → 50% of $60 = $30
        self.assertAlmostEqual(
            calculate_lesson_charge(self._lesson(60.0, "Late Cancel"), self._POLICY), 30.0
        )

    def test_cancelled_applies_none_policy_charge(self):
        from backend.app.domain.invoice import calculate_lesson_charge
        # Cancelled → cancel_charge_type=none → $0
        self.assertAlmostEqual(
            calculate_lesson_charge(self._lesson(60.0, "Cancelled"), self._POLICY), 0.0
        )

    def test_absent_without_policy_charges_full_rate(self):
        from backend.app.domain.invoice import calculate_lesson_charge
        # No policy → fall back to full rate
        self.assertAlmostEqual(
            calculate_lesson_charge(self._lesson(60.0, "Absent"), None), 60.0
        )

    def test_lesson_level_policy_takes_priority_over_default(self):
        from backend.app.domain.invoice import calculate_lesson_charge
        lesson_policy = {"absent_charge_type": "flat", "absent_charge_value": 5}
        default_policy = {"absent_charge_type": "flat", "absent_charge_value": 100}
        lesson = {**self._lesson(60.0, "Absent"), "attendance_policy": lesson_policy}
        self.assertAlmostEqual(calculate_lesson_charge(lesson, default_policy), 5.0)


class TestInvoiceDomainBuildLineItems(unittest.TestCase):
    """domain/invoice — build_line_items()"""

    def test_returns_one_item_per_lesson(self):
        from backend.app.domain.invoice import build_line_items
        lessons = [
            {"lesson_id": f"l{i}", "start_time": f"2025-01-0{i+1}T10:00:00", "rate": 50.0}
            for i in range(3)
        ]
        items, total = build_line_items(lessons, None)
        self.assertEqual(len(items), 3)

    def test_total_equals_sum_of_item_amounts(self):
        from backend.app.domain.invoice import build_line_items
        lessons = [
            {"lesson_id": "l1", "start_time": "2025-01-01T10:00:00", "rate": 40.0},
            {"lesson_id": "l2", "start_time": "2025-01-08T10:00:00", "rate": 60.0},
        ]
        items, total = build_line_items(lessons, None)
        self.assertAlmostEqual(total, 100.0)
        self.assertAlmostEqual(sum(i["amount"] for i in items), total)

    def test_description_includes_lesson_date(self):
        from backend.app.domain.invoice import build_line_items
        lessons = [{"lesson_id": "l1", "start_time": "2025-03-15T10:00:00", "rate": 50.0}]
        items, _ = build_line_items(lessons, None)
        self.assertIn("2025-03-15", items[0]["description"])

    def test_excused_lesson_produces_zero_amount_item(self):
        from backend.app.domain.invoice import build_line_items
        lessons = [{"lesson_id": "l1", "start_time": "2025-01-01T10:00:00",
                    "rate": 80.0, "attendance_status": "Excused"}]
        items, total = build_line_items(lessons, None)
        self.assertEqual(items[0]["amount"], 0.0)
        self.assertEqual(total, 0.0)

    def test_empty_lessons_returns_empty_list_and_zero_total(self):
        from backend.app.domain.invoice import build_line_items
        items, total = build_line_items([], None)
        self.assertEqual(items, [])
        self.assertEqual(total, 0.0)


class TestInvoiceDomainOutstandingBalance(unittest.TestCase):
    """domain/invoice — compute_outstanding_balance()"""

    def test_sums_unpaid_portions_of_all_invoices(self):
        from backend.app.domain.invoice import compute_outstanding_balance
        invoices = [
            {"total_amount": 100.0, "amount_paid": 40.0},
            {"total_amount": 200.0, "amount_paid": 0.0},
        ]
        self.assertAlmostEqual(compute_outstanding_balance(invoices), 260.0)

    def test_fully_paid_invoices_contribute_zero(self):
        from backend.app.domain.invoice import compute_outstanding_balance
        invoices = [{"total_amount": 100.0, "amount_paid": 100.0}]
        self.assertAlmostEqual(compute_outstanding_balance(invoices), 0.0)

    def test_empty_list_returns_zero(self):
        from backend.app.domain.invoice import compute_outstanding_balance
        self.assertEqual(compute_outstanding_balance([]), 0.0)


# ── domain/payment.py ─────────────────────────────────────────────────────────

def _invoice(status="Pending", total=100.0, paid=0.0):
    return {"invoice_id": "inv-1", "status": status, "total_amount": total, "amount_paid": paid}


class TestPaymentDomainValidation(unittest.TestCase):
    """domain/payment — validate_payment_request()"""

    def test_cancelled_invoice_raises(self):
        from backend.app.domain.payment import validate_payment_request
        with self.assertRaises(InvoiceCancelledError):
            validate_payment_request(_invoice(status="Cancelled"), 50.0)

    def test_already_paid_invoice_raises(self):
        from backend.app.domain.payment import validate_payment_request
        with self.assertRaises(InvoiceAlreadyPaidError):
            validate_payment_request(_invoice(status="Paid", total=100.0, paid=100.0), 10.0)

    def test_overpayment_raises(self):
        from backend.app.domain.payment import validate_payment_request
        with self.assertRaises(OverpaymentError):
            validate_payment_request(_invoice(total=100.0, paid=80.0), 50.0)

    def test_exact_payment_of_outstanding_passes(self):
        from backend.app.domain.payment import validate_payment_request
        validate_payment_request(_invoice(total=100.0, paid=60.0), 40.0)  # no raise

    def test_partial_payment_within_outstanding_passes(self):
        from backend.app.domain.payment import validate_payment_request
        validate_payment_request(_invoice(total=100.0, paid=0.0), 50.0)  # no raise


class TestPaymentDomainComputeApply(unittest.TestCase):
    """domain/payment — compute_apply_amount()"""

    def test_caps_at_outstanding_when_requested_exceeds(self):
        from backend.app.domain.payment import compute_apply_amount
        result = compute_apply_amount(_invoice(total=100.0, paid=70.0), 200.0)
        self.assertAlmostEqual(result, 30.0)

    def test_returns_full_requested_when_within_outstanding(self):
        from backend.app.domain.payment import compute_apply_amount
        result = compute_apply_amount(_invoice(total=100.0, paid=0.0), 50.0)
        self.assertAlmostEqual(result, 50.0)

    def test_returns_zero_when_already_paid_in_full(self):
        from backend.app.domain.payment import compute_apply_amount
        result = compute_apply_amount(_invoice(total=100.0, paid=100.0), 50.0)
        self.assertEqual(result, 0.0)


class TestPaymentDomainInvoiceStatus(unittest.TestCase):
    """domain/payment — determine_invoice_status()"""

    def test_returns_paid_when_fully_covered(self):
        from backend.app.domain.payment import determine_invoice_status
        self.assertEqual(determine_invoice_status(100.0, 100.0, "Pending"), "Paid")

    def test_returns_paid_when_overpaid(self):
        from backend.app.domain.payment import determine_invoice_status
        self.assertEqual(determine_invoice_status(100.0, 110.0, "Pending"), "Paid")

    def test_keeps_current_status_when_not_fully_paid(self):
        from backend.app.domain.payment import determine_invoice_status
        self.assertEqual(determine_invoice_status(100.0, 60.0, "Pending"), "Pending")

    def test_keeps_current_status_when_no_payment_applied(self):
        from backend.app.domain.payment import determine_invoice_status
        self.assertEqual(determine_invoice_status(100.0, 0.0, "Pending"), "Pending")


# ── domain/scheduling.py ──────────────────────────────────────────────────────

class TestSchedulingDomain(unittest.TestCase):
    """domain/scheduling — conflict validation rules."""

    def test_no_instructor_conflict_passes(self):
        from backend.app.domain.scheduling import validate_no_instructor_conflict
        validate_no_instructor_conflict([])  # no raise

    def test_instructor_conflict_raises(self):
        from backend.app.domain.scheduling import validate_no_instructor_conflict
        with self.assertRaises(InstructorUnavailableError):
            validate_no_instructor_conflict([{"lesson_id": "l1"}])

    def test_no_room_conflict_passes(self):
        from backend.app.domain.scheduling import validate_no_room_conflict
        validate_no_room_conflict([])  # no raise

    def test_room_conflict_raises(self):
        from backend.app.domain.scheduling import validate_no_room_conflict
        with self.assertRaises(RoomUnavailableError):
            validate_no_room_conflict([{"lesson_id": "l2"}])

    def test_multiple_instructor_conflicts_still_raises_once(self):
        from backend.app.domain.scheduling import validate_no_instructor_conflict
        conflicts = [{"lesson_id": "l1"}, {"lesson_id": "l2"}]
        with self.assertRaises(InstructorUnavailableError):
            validate_no_instructor_conflict(conflicts)


# ── domain/person.py ──────────────────────────────────────────────────────────

class TestPersonDomainPrepareCreate(unittest.TestCase):
    """domain/person — prepare_person_linked_create() two-mode creation."""

    def test_mode_a_extracts_person_fields_when_no_person_id(self):
        from backend.app.domain.person import prepare_person_linked_create
        person_fields, entity_data = prepare_person_linked_create(
            {"name": "Alice", "email": "a@b.com", "phone": "555", "client_id": "c1"}
        )
        self.assertEqual(person_fields, {"name": "Alice", "email": "a@b.com", "phone": "555"})
        self.assertNotIn("name", entity_data)
        self.assertEqual(entity_data["client_id"], "c1")

    def test_mode_a_raises_when_name_missing(self):
        from backend.app.domain.person import prepare_person_linked_create
        with self.assertRaises(ValidationError) as ctx:
            prepare_person_linked_create({"email": "a@b.com"})
        self.assertIn("name", [e["field"] for e in ctx.exception.errors])

    def test_mode_a_raises_when_name_is_empty_string(self):
        from backend.app.domain.person import prepare_person_linked_create
        with self.assertRaises(ValidationError):
            prepare_person_linked_create({"name": ""})

    def test_mode_b_returns_none_person_fields_when_person_id_given(self):
        from backend.app.domain.person import prepare_person_linked_create
        person_fields, entity_data = prepare_person_linked_create(
            {"person_id": "p1", "name": "Ignored", "client_id": "c1"}
        )
        self.assertIsNone(person_fields)
        self.assertNotIn("name", entity_data)
        self.assertEqual(entity_data["person_id"], "p1")

    def test_mode_b_strips_all_person_fields(self):
        from backend.app.domain.person import prepare_person_linked_create
        person_fields, entity_data = prepare_person_linked_create(
            {"person_id": "p1", "name": "X", "email": "x@x.com", "phone": "000"}
        )
        self.assertIsNone(person_fields)
        for key in ("name", "email", "phone"):
            self.assertNotIn(key, entity_data)

    def test_mode_a_partial_person_data_is_accepted(self):
        """Name is required; email and phone are optional."""
        from backend.app.domain.person import prepare_person_linked_create
        person_fields, _ = prepare_person_linked_create({"name": "Bob"})
        self.assertEqual(person_fields, {"name": "Bob"})

    def test_returned_dicts_are_independent_copies(self):
        """Mutations to the returned dicts must not affect each other."""
        from backend.app.domain.person import prepare_person_linked_create
        original = {"name": "Carol", "client_id": "c1"}
        person_fields, entity_data = prepare_person_linked_create(original)
        entity_data["extra"] = "injected"
        self.assertNotIn("extra", person_fields or {})


class TestPersonDomainExtractUpdateFields(unittest.TestCase):
    """domain/person — extract_person_update_fields()"""

    def test_separates_person_and_entity_fields(self):
        from backend.app.domain.person import extract_person_update_fields
        person_fields, entity_data = extract_person_update_fields(
            {"name": "New Name", "email": "n@n.com", "credits": 50.0}
        )
        self.assertEqual(person_fields, {"name": "New Name", "email": "n@n.com"})
        self.assertEqual(entity_data, {"credits": 50.0})

    def test_all_person_fields_absent_returns_empty_person_dict(self):
        from backend.app.domain.person import extract_person_update_fields
        person_fields, entity_data = extract_person_update_fields({"credits": 10.0})
        self.assertEqual(person_fields, {})
        self.assertEqual(entity_data, {"credits": 10.0})

    def test_only_person_fields_present(self):
        from backend.app.domain.person import extract_person_update_fields
        person_fields, entity_data = extract_person_update_fields({"name": "Dave"})
        self.assertEqual(person_fields, {"name": "Dave"})
        self.assertEqual(entity_data, {})

    def test_phone_is_treated_as_person_field(self):
        from backend.app.domain.person import extract_person_update_fields
        person_fields, _ = extract_person_update_fields({"phone": "555-1234"})
        self.assertIn("phone", person_fields)


if __name__ == "__main__":
    unittest.main()
