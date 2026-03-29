"""
Unit tests covering:
  FR-11 — Invoice Generation: monthly invoices from completed/scheduled lessons
  FR-12 — Payment Recording: record payments, track outstanding balances
"""
import unittest
from unittest.mock import MagicMock

from backend.app.domain.exceptions.exceptions import DuplicateInvoiceError, NoLessonsFoundError
from backend.app.domain.exceptions.exceptions import (
    InvalidPaymentAmountError,
    InvoiceAlreadyPaidError,
    InvoiceCancelledError,
    InvoiceNotFoundError,
    OverpaymentError,
)
from backend.app.infrastructure.database.database import DatabaseConnection


def _mock_db():
    inst = MagicMock()
    client = MagicMock()
    inst.client = client
    DatabaseConnection._instance = inst
    return client


# ── FR-11: generate_monthly_invoice ──────────────────────────────────────────

class TestGenerateMonthlyInvoice(unittest.TestCase):

    def setUp(self):
        self.client = _mock_db()

    def tearDown(self):
        DatabaseConnection._instance = None

    def _configure(self, check_result, lessons, invoice_row=None):
        """Wire the mock DB for the table calls made during invoice generation.

        Query order:
          1. invoice SELECT  — duplicate check
          2. lesson_enrollment SELECT — get lesson_ids for student
          3. lesson SELECT   — filter by lesson_ids, status, date range
          4. invoice INSERT  — create header
          5. invoice_line INSERT (absorbed by default MagicMock)
        """
        counts = {"invoice": 0}
        enrollment_rows = [{"lesson_id": l["lesson_id"]} for l in lessons]

        def side_effect(name):
            m = MagicMock()
            if name == "invoice":
                counts["invoice"] += 1
                if counts["invoice"] == 1:
                    # duplicate-check SELECT
                    m.select.return_value.eq.return_value.eq.return_value \
                        .execute.return_value.data = check_result
                else:
                    # INSERT header
                    m.insert.return_value.execute.return_value.data = \
                        [invoice_row] if invoice_row else []
            elif name == "lesson_enrollment":
                # SELECT lesson_id … eq("student_id", …)
                m.select.return_value.eq.return_value.execute.return_value.data = enrollment_rows
            elif name == "lesson":
                # SELECT … in_("lesson_id") .in_("status") .gte() .lte()
                m.select.return_value.in_.return_value.in_.return_value \
                    .gte.return_value.lte.return_value.execute.return_value.data = lessons
            elif name == "student":
                # Student.get(student_id) — return no client so credits block is skipped
                m.select.return_value.eq.return_value.execute.return_value.data = \
                    [{"student_id": "s1", "client_id": None}]
            # invoice_line insert absorbed by default MagicMock
            return m

        self.client.table.side_effect = side_effect

    def test_raises_when_invoice_already_exists(self):
        """FR-11: Duplicate invoice for the same student/period is rejected."""
        from backend.app.application.services import generate_monthly_invoice
        self._configure(check_result=[{"invoice_id": "existing-1"}], lessons=[])
        with self.assertRaises(DuplicateInvoiceError) as ctx:
            generate_monthly_invoice("s1", 2025, 1)
        self.assertIn("already exists", str(ctx.exception))

    def test_raises_when_no_qualifying_lessons(self):
        """FR-11: Invoice cannot be generated without Completed/Scheduled lessons."""
        from backend.app.application.services import generate_monthly_invoice
        self._configure(check_result=[], lessons=[])
        with self.assertRaises(NoLessonsFoundError) as ctx:
            generate_monthly_invoice("s1", 2025, 1)
        self.assertIn("No Completed or Scheduled lessons", str(ctx.exception))

    def test_result_contains_invoice_and_line_items_keys(self):
        """FR-11: Returned dict has 'invoice' and 'line_items' keys."""
        from backend.app.application.services import generate_monthly_invoice
        lessons = [{"lesson_id": "l1", "start_time": "2025-01-10T10:00:00", "rate": 50.0}]
        row = {"invoice_id": "inv-1", "total_amount": 50.0, "status": "Pending"}
        self._configure(check_result=[], lessons=lessons, invoice_row=row)
        result = generate_monthly_invoice("s1", 2025, 1)
        self.assertIn("invoice", result)
        self.assertIn("line_items", result)

    def test_one_line_item_per_lesson(self):
        """FR-11: Each qualifying lesson produces exactly one line item."""
        from backend.app.application.services import generate_monthly_invoice
        lessons = [
            {"lesson_id": f"l{i}", "start_time": f"2025-01-0{i+1}T10:00:00", "rate": 50.0}
            for i in range(3)
        ]
        row = {"invoice_id": "inv-1", "total_amount": 150.0}
        self._configure(check_result=[], lessons=lessons, invoice_row=row)
        result = generate_monthly_invoice("s1", 2025, 1)
        self.assertEqual(len(result["line_items"]), 3)

    def test_line_item_amounts_sum_to_total(self):
        """FR-11: Sum of line-item amounts equals total invoice value."""
        from backend.app.application.services import generate_monthly_invoice
        lessons = [
            {"lesson_id": "l1", "start_time": "2025-01-10T10:00:00", "rate": 40.0},
            {"lesson_id": "l2", "start_time": "2025-01-17T10:00:00", "rate": 60.0},
        ]
        row = {"invoice_id": "inv-1", "total_amount": 100.0}
        self._configure(check_result=[], lessons=lessons, invoice_row=row)
        result = generate_monthly_invoice("s1", 2025, 1)
        total = sum(li["amount"] for li in result["line_items"])
        self.assertAlmostEqual(total, 100.0)

    def test_invoice_status_is_pending(self):
        """FR-11: Newly generated invoices are created with status 'Pending'."""
        from backend.app.application.services import generate_monthly_invoice
        lessons = [{"lesson_id": "l1", "start_time": "2025-01-10T10:00:00", "rate": 50.0}]
        row = {"invoice_id": "inv-1", "status": "Pending", "total_amount": 50.0}
        self._configure(check_result=[], lessons=lessons, invoice_row=row)
        result = generate_monthly_invoice("s1", 2025, 1)
        self.assertEqual(result["invoice"]["status"], "Pending")

    def test_period_covers_full_calendar_month(self):
        """FR-11: period_start is the 1st and period_end is the last day of the month."""
        from backend.app.application.services import generate_monthly_invoice
        lessons = [{"lesson_id": "l1", "start_time": "2025-03-15T10:00:00", "rate": 50.0}]
        row = {
            "invoice_id": "inv-1",
            "period_start": "2025-03-01",
            "period_end": "2025-03-31",
            "total_amount": 50.0,
        }
        self._configure(check_result=[], lessons=lessons, invoice_row=row)
        result = generate_monthly_invoice("s1", 2025, 3)
        self.assertEqual(result["invoice"]["period_start"], "2025-03-01")
        self.assertEqual(result["invoice"]["period_end"], "2025-03-31")

    def test_february_non_leap_year_ends_on_28th(self):
        """FR-11: February 2025 period ends on the 28th (non-leap year)."""
        from backend.app.application.services import generate_monthly_invoice
        lessons = [{"lesson_id": "l1", "start_time": "2025-02-14T10:00:00", "rate": 50.0}]
        row = {
            "invoice_id": "inv-1",
            "period_start": "2025-02-01",
            "period_end": "2025-02-28",
            "total_amount": 50.0,
        }
        self._configure(check_result=[], lessons=lessons, invoice_row=row)
        result = generate_monthly_invoice("s1", 2025, 2)
        self.assertEqual(result["invoice"]["period_end"], "2025-02-28")

    def test_line_item_description_includes_lesson_date(self):
        """FR-11: Each line item description references the lesson date."""
        from backend.app.application.services import generate_monthly_invoice
        lessons = [{"lesson_id": "l1", "start_time": "2025-01-10T10:00:00", "rate": 50.0}]
        row = {"invoice_id": "inv-1", "total_amount": 50.0}
        self._configure(check_result=[], lessons=lessons, invoice_row=row)
        result = generate_monthly_invoice("s1", 2025, 1)
        self.assertIn("2025-01-10", result["line_items"][0]["description"])


# ── FR-12: get_outstanding_balance ────────────────────────────────────────────

class TestOutstandingBalance(unittest.TestCase):

    def setUp(self):
        self.client = _mock_db()

    def tearDown(self):
        DatabaseConnection._instance = None

    def test_sums_pending_invoices_correctly(self):
        """FR-12: Outstanding balance = sum of (total - paid) for all Pending invoices."""
        from backend.app.application.services import get_outstanding_balance
        pending = [
            {"invoice_id": "i1", "total_amount": 100.0, "amount_paid": 50.0},
            {"invoice_id": "i2", "total_amount": 200.0, "amount_paid": 0.0},
        ]
        self.client.table.return_value.select.return_value.eq.return_value \
            .execute.return_value.data = pending
        result = get_outstanding_balance()
        self.assertAlmostEqual(result["total_outstanding_balance"], 250.0)
        self.assertEqual(len(result["invoices"]), 2)

    def test_no_pending_invoices_returns_zero(self):
        """FR-12: No pending invoices → total outstanding is 0."""
        from backend.app.application.services import get_outstanding_balance
        self.client.table.return_value.select.return_value.eq.return_value \
            .execute.return_value.data = []
        result = get_outstanding_balance()
        self.assertEqual(result["total_outstanding_balance"], 0.0)
        self.assertEqual(result["invoices"], [])


# ── FR-12: record_payment ─────────────────────────────────────────────────────

class TestRecordPayment(unittest.TestCase):

    def setUp(self):
        self.client = _mock_db()

    def tearDown(self):
        DatabaseConnection._instance = None

    def _invoice(self, status="Pending", total=100.0, paid=0.0):
        return {"invoice_id": "inv-1", "total_amount": total, "amount_paid": paid, "status": status}

    def _mock_invoice_fetch(self, invoice):
        self.client.table.return_value.select.return_value.eq.return_value \
            .execute.return_value.data = [invoice]

    def test_requires_invoice_id(self):
        from backend.app.application.services import record_payment
        with self.assertRaises(InvalidPaymentAmountError) as ctx:
            record_payment({"amount": 50.0})
        self.assertIn("invoice_id", str(ctx.exception.errors))

    def test_requires_positive_amount(self):
        from backend.app.application.services import record_payment
        with self.assertRaises(InvalidPaymentAmountError):
            record_payment({"invoice_id": "inv-1", "amount": 0})

    def test_rejects_negative_amount(self):
        from backend.app.application.services import record_payment
        with self.assertRaises(InvalidPaymentAmountError):
            record_payment({"invoice_id": "inv-1", "amount": -10.0})

    def test_raises_if_invoice_not_found(self):
        from backend.app.application.services import record_payment
        self.client.table.return_value.select.return_value.eq.return_value \
            .execute.return_value.data = []
        with self.assertRaises(InvoiceNotFoundError) as ctx:
            record_payment({"invoice_id": "inv-999", "amount": 50.0})
        self.assertIn("Invoice not found", str(ctx.exception))

    def test_raises_on_cancelled_invoice(self):
        from backend.app.application.services import record_payment
        self._mock_invoice_fetch(self._invoice(status="Cancelled"))
        with self.assertRaises(InvoiceCancelledError) as ctx:
            record_payment({"invoice_id": "inv-1", "amount": 50.0})
        self.assertIn("cancelled", str(ctx.exception).lower())

    def test_raises_on_already_paid_invoice(self):
        from backend.app.application.services import record_payment
        self._mock_invoice_fetch(self._invoice(status="Paid", total=100.0, paid=100.0))
        with self.assertRaises(InvoiceAlreadyPaidError) as ctx:
            record_payment({"invoice_id": "inv-1", "amount": 10.0})
        self.assertIn("fully paid", str(ctx.exception).lower())

    def test_raises_when_payment_exceeds_outstanding(self):
        from backend.app.application.services import record_payment
        self._mock_invoice_fetch(self._invoice(total=100.0, paid=80.0))
        with self.assertRaises(OverpaymentError) as ctx:
            record_payment({"invoice_id": "inv-1", "amount": 50.0})
        self.assertIn("exceeds outstanding balance", str(ctx.exception))

    def test_successful_payment_returns_payment_record(self):
        """FR-12: A valid payment is persisted and returned."""
        from backend.app.application.services import record_payment
        invoice = self._invoice(total=100.0, paid=0.0)
        payment_row = {"payment_id": "p1", "invoice_id": "inv-1", "amount": 100.0}
        counts = {"invoice": 0}

        def side_effect(name):
            m = MagicMock()
            if name == "invoice":
                counts["invoice"] += 1
                if counts["invoice"] == 1:
                    m.select.return_value.eq.return_value.execute.return_value.data = [invoice]
            elif name == "payment":
                m.insert.return_value.execute.return_value.data = [payment_row]
            return m

        self.client.table.side_effect = side_effect
        result = record_payment({"invoice_id": "inv-1", "amount": 100.0})
        self.assertEqual(result["payment_id"], "p1")

    def test_default_payment_method_is_card(self):
        """FR-12: When payment_method is omitted, 'Card' is used."""
        from backend.app.application.services import record_payment
        invoice = self._invoice(total=100.0, paid=0.0)
        inserted_data = {}
        counts = {"invoice": 0}

        def side_effect(name):
            m = MagicMock()
            if name == "invoice":
                counts["invoice"] += 1
                if counts["invoice"] == 1:
                    m.select.return_value.eq.return_value.execute.return_value.data = [invoice]
            elif name == "payment":
                def capture_insert(data):
                    inserted_data.update(data)
                    mm = MagicMock()
                    mm.execute.return_value.data = [{"payment_id": "p1", **data}]
                    return mm
                m.insert.side_effect = capture_insert
            return m

        self.client.table.side_effect = side_effect
        record_payment({"invoice_id": "inv-1", "amount": 50.0})
        self.assertEqual(inserted_data.get("payment_method"), "Card")


if __name__ == "__main__":
    unittest.main()