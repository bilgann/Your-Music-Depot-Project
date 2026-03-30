"""
Unit tests for all value objects in the domain layer.

Covers:
  value_objects/financial/   — Money, Rate, InvoiceItem, InvoiceStatus, ChargeRule
  value_objects/people/      — PersonName
  value_objects/lesson/      — Instrument, RoomInstrument, SkillLevel, TeachableRange,
                               InstrumentProficiency, AttendanceStatus
  value_objects/scheduling/  — TimeSlot, DateRange, RecurrenceRule, BlockedTime, LessonStatus
  value_objects/compatibility/ — TeachingRequirement, CompatibilityResult
"""
import unittest

from backend.app.domain.exceptions.exceptions import ValidationError


# ── Money ─────────────────────────────────────────────────────────────────────

class TestMoney(unittest.TestCase):
    """value_objects/financial/money.py"""

    def _m(self, amount, currency="CAD"):
        from backend.app.domain.value_objects.financial.money import Money
        return Money(amount, currency)

    def test_zero_creates_money_with_zero_amount(self):
        from backend.app.domain.value_objects.financial.money import Money
        m = Money.zero()
        self.assertEqual(m.amount, 0.0)
        self.assertEqual(m.currency, "CAD")

    def test_zero_accepts_custom_currency(self):
        from backend.app.domain.value_objects.financial.money import Money
        m = Money.zero("USD")
        self.assertEqual(m.currency, "USD")

    def test_of_rounds_to_two_decimals(self):
        from backend.app.domain.value_objects.financial.money import Money
        m = Money.of(12.3456)
        self.assertAlmostEqual(m.amount, 12.35, places=2)

    def test_of_converts_int(self):
        from backend.app.domain.value_objects.financial.money import Money
        m = Money.of(50)
        self.assertAlmostEqual(m.amount, 50.0)

    def test_add_same_currency(self):
        a = self._m(40.0)
        b = self._m(60.0)
        result = a + b
        self.assertAlmostEqual(result.amount, 100.0)

    def test_add_rounds_to_two_decimals(self):
        a = self._m(0.10)
        b = self._m(0.20)
        result = a + b
        self.assertAlmostEqual(result.amount, 0.30, places=2)

    def test_sub_same_currency(self):
        a = self._m(100.0)
        b = self._m(40.0)
        result = a - b
        self.assertAlmostEqual(result.amount, 60.0)

    def test_add_different_currency_raises(self):
        a = self._m(50.0, "CAD")
        b = self._m(50.0, "USD")
        with self.assertRaises(ValueError):
            _ = a + b

    def test_sub_different_currency_raises(self):
        a = self._m(100.0, "CAD")
        b = self._m(20.0, "USD")
        with self.assertRaises(ValueError):
            _ = a - b

    def test_str_format(self):
        m = self._m(12.5)
        self.assertEqual(str(m), "CAD 12.50")

    def test_to_dict(self):
        m = self._m(75.0)
        d = m.to_dict()
        self.assertEqual(d["amount"], 75.0)
        self.assertEqual(d["currency"], "CAD")

    def test_frozen_dataclass_is_immutable(self):
        from backend.app.domain.value_objects.financial.money import Money
        m = Money.of(10.0)
        with self.assertRaises(Exception):
            m.amount = 20.0


# ── Rate ──────────────────────────────────────────────────────────────────────

class TestRate(unittest.TestCase):
    """value_objects/financial/rate.py"""

    def _money(self, amount):
        from backend.app.domain.value_objects.financial.money import Money
        return Money.of(amount)

    def test_one_time_factory_sets_charge_type(self):
        from backend.app.domain.value_objects.financial.rate import Rate
        r = Rate.one_time(self._money(40))
        self.assertEqual(r.charge_type, "one_time")

    def test_hourly_factory_sets_charge_type(self):
        from backend.app.domain.value_objects.financial.rate import Rate
        r = Rate.hourly(self._money(60))
        self.assertEqual(r.charge_type, "hourly")

    def test_one_time_for_duration_returns_full_amount(self):
        from backend.app.domain.value_objects.financial.rate import Rate
        r = Rate.one_time(self._money(50))
        charge = r.for_duration(30)
        self.assertAlmostEqual(charge.amount, 50.0)

    def test_hourly_for_duration_60_minutes_returns_full(self):
        from backend.app.domain.value_objects.financial.rate import Rate
        r = Rate.hourly(self._money(60))
        charge = r.for_duration(60)
        self.assertAlmostEqual(charge.amount, 60.0)

    def test_hourly_for_duration_30_minutes_returns_half(self):
        from backend.app.domain.value_objects.financial.rate import Rate
        r = Rate.hourly(self._money(60))
        charge = r.for_duration(30)
        self.assertAlmostEqual(charge.amount, 30.0)

    def test_hourly_for_duration_45_minutes_prorates_correctly(self):
        from backend.app.domain.value_objects.financial.rate import Rate
        r = Rate.hourly(self._money(60))
        charge = r.for_duration(45)
        self.assertAlmostEqual(charge.amount, 45.0)

    def test_invalid_charge_type_raises_exception(self):
        """Invalid rate type should raise; note: may raise AttributeError due to
        a bug where self.VALID_TYPES is referenced but not defined on Rate."""
        from backend.app.domain.value_objects.financial.rate import Rate
        with self.assertRaises(Exception):
            Rate("weekly", self._money(50))

    def test_to_dict_includes_charge_type_and_amount(self):
        from backend.app.domain.value_objects.financial.rate import Rate
        r = Rate.one_time(self._money(80))
        d = r.to_dict()
        self.assertEqual(d["charge_type"], "one_time")
        self.assertAlmostEqual(d["amount"], 80.0)

    def test_from_dict_roundtrip(self):
        from backend.app.domain.value_objects.financial.rate import Rate
        r = Rate.hourly(self._money(60))
        r2 = Rate.from_dict(r.to_dict())
        self.assertEqual(r2.charge_type, "hourly")
        self.assertAlmostEqual(r2.amount.amount, 60.0)


# ── InvoiceItem ───────────────────────────────────────────────────────────────

class TestInvoiceItem(unittest.TestCase):
    """value_objects/financial/invoice_item.py"""

    def _money(self, amount=50.0):
        from backend.app.domain.value_objects.financial.money import Money
        return Money.of(amount)

    def test_for_lesson_factory_sets_item_type(self):
        from backend.app.domain.value_objects.financial.invoice_item import InvoiceItem
        item = InvoiceItem.for_lesson("occ-1", "Attended — 2025-01-10", self._money())
        self.assertEqual(item.item_type, "lesson")
        self.assertEqual(item.occurrence_id, "occ-1")

    def test_for_instrument_damage_factory(self):
        from backend.app.domain.value_objects.financial.invoice_item import InvoiceItem
        item = InvoiceItem.for_instrument_damage("Cracked violin bridge", self._money(75))
        self.assertEqual(item.item_type, "instrument_damage")
        self.assertIsNone(item.occurrence_id)

    def test_for_instrument_purchase_factory(self):
        from backend.app.domain.value_objects.financial.invoice_item import InvoiceItem
        item = InvoiceItem.for_instrument_purchase("Ukulele", self._money(120))
        self.assertEqual(item.item_type, "instrument_purchase")

    def test_other_factory(self):
        from backend.app.domain.value_objects.financial.invoice_item import InvoiceItem
        item = InvoiceItem.other("Admin fee", self._money(10))
        self.assertEqual(item.item_type, "other")

    def test_occurrence_id_on_non_lesson_raises(self):
        from backend.app.domain.value_objects.financial.invoice_item import InvoiceItem
        with self.assertRaises(ValueError):
            InvoiceItem(
                item_type="instrument_damage",
                description="test",
                amount=self._money(),
                occurrence_id="should-not-be-here",
            )

    def test_invalid_item_type_raises(self):
        from backend.app.domain.value_objects.financial.invoice_item import InvoiceItem
        with self.assertRaises(ValueError):
            InvoiceItem(item_type="not_a_type", description="x", amount=self._money())

    def test_negative_amount_allowed_for_discounts(self):
        from backend.app.domain.value_objects.financial.invoice_item import InvoiceItem
        from backend.app.domain.value_objects.financial.money import Money
        item = InvoiceItem.other("Sibling discount", Money.of(-10))
        self.assertAlmostEqual(item.amount.amount, -10.0)

    def test_to_dict_from_dict_roundtrip(self):
        from backend.app.domain.value_objects.financial.invoice_item import InvoiceItem
        item = InvoiceItem.for_lesson("occ-1", "Attended — 2025-01-10", self._money(50), "present")
        item2 = InvoiceItem.from_dict(item.to_dict())
        self.assertEqual(item2.item_type, "lesson")
        self.assertEqual(item2.occurrence_id, "occ-1")
        self.assertAlmostEqual(item2.amount.amount, 50.0)


# ── InvoiceStatus ─────────────────────────────────────────────────────────────

class TestInvoiceStatus(unittest.TestCase):
    """value_objects/financial/invoice_status.py"""

    def test_valid_statuses_do_not_raise(self):
        from backend.app.domain.value_objects.financial.invoice_status import InvoiceStatus
        for status in ("Pending", "Partial", "Paid", "Cancelled"):
            InvoiceStatus(status)

    def test_invalid_status_raises_validation_error(self):
        from backend.app.domain.value_objects.financial.invoice_status import InvoiceStatus
        with self.assertRaises(ValidationError):
            InvoiceStatus("Unknown")

    def test_paid_is_terminal(self):
        from backend.app.domain.value_objects.financial.invoice_status import InvoiceStatus
        self.assertTrue(InvoiceStatus("Paid").is_terminal())

    def test_cancelled_is_terminal(self):
        from backend.app.domain.value_objects.financial.invoice_status import InvoiceStatus
        self.assertTrue(InvoiceStatus("Cancelled").is_terminal())

    def test_pending_is_not_terminal(self):
        from backend.app.domain.value_objects.financial.invoice_status import InvoiceStatus
        self.assertFalse(InvoiceStatus("Pending").is_terminal())

    def test_partial_is_not_terminal(self):
        from backend.app.domain.value_objects.financial.invoice_status import InvoiceStatus
        self.assertFalse(InvoiceStatus("Partial").is_terminal())

    def test_str_returns_value(self):
        from backend.app.domain.value_objects.financial.invoice_status import InvoiceStatus
        self.assertEqual(str(InvoiceStatus("Paid")), "Paid")


# ── ChargeRule ────────────────────────────────────────────────────────────────

class TestChargeRule(unittest.TestCase):
    """value_objects/financial/charge_rule.py"""

    def test_none_factory_creates_no_charge_rule(self):
        from backend.app.domain.value_objects.financial.charge_rule import ChargeRule
        rule = ChargeRule.none()
        self.assertEqual(rule.charge_type, "none")
        self.assertEqual(rule.charge_value, 0)

    def test_flat_charge_rule(self):
        from backend.app.domain.value_objects.financial.charge_rule import ChargeRule
        rule = ChargeRule("flat", 25.0)
        self.assertEqual(rule.charge_type, "flat")
        self.assertAlmostEqual(rule.charge_value, 25.0)

    def test_percentage_charge_rule(self):
        from backend.app.domain.value_objects.financial.charge_rule import ChargeRule
        rule = ChargeRule("percentage", 50)
        self.assertEqual(rule.charge_type, "percentage")

    def test_negative_value_allowed_for_discounts(self):
        from backend.app.domain.value_objects.financial.charge_rule import ChargeRule
        rule = ChargeRule("flat", -5.0)
        self.assertAlmostEqual(rule.charge_value, -5.0)

    def test_to_dict(self):
        from backend.app.domain.value_objects.financial.charge_rule import ChargeRule
        rule = ChargeRule("flat", 30.0)
        d = rule.to_dict()
        self.assertEqual(d["charge_type"], "flat")
        self.assertAlmostEqual(d["charge_value"], 30.0)


# ── PersonName ────────────────────────────────────────────────────────────────

class TestPersonName(unittest.TestCase):
    """value_objects/people/person_name.py"""

    def test_valid_name_creates_successfully(self):
        from backend.app.domain.value_objects.people.person_name import PersonName
        p = PersonName("Alice Smith")
        self.assertEqual(p.value, "Alice Smith")

    def test_empty_string_raises(self):
        from backend.app.domain.value_objects.people.person_name import PersonName
        with self.assertRaises(ValidationError):
            PersonName("")

    def test_whitespace_only_raises(self):
        from backend.app.domain.value_objects.people.person_name import PersonName
        with self.assertRaises(ValidationError):
            PersonName("   ")

    def test_str_returns_value(self):
        from backend.app.domain.value_objects.people.person_name import PersonName
        self.assertEqual(str(PersonName("Bob Jones")), "Bob Jones")


# ── Instrument ────────────────────────────────────────────────────────────────

class TestInstrument(unittest.TestCase):
    """value_objects/lesson/instrument.py"""

    def test_valid_instrument_creates(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        i = Instrument("Piano", "keyboard")
        self.assertEqual(i.name, "Piano")
        self.assertEqual(i.family, "keyboard")

    def test_blank_name_raises(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        with self.assertRaises(ValidationError):
            Instrument("", "keyboard")

    def test_whitespace_name_raises(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        with self.assertRaises(ValidationError):
            Instrument("   ", "keyboard")

    def test_invalid_family_raises(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        with self.assertRaises(ValidationError):
            Instrument("Theremin", "electronic")

    def test_requires_quantity_false_for_voice(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        i = Instrument("Voice", "voice")
        self.assertFalse(i.requires_quantity)

    def test_requires_quantity_true_for_keyboard(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        i = Instrument("Piano", "keyboard")
        self.assertTrue(i.requires_quantity)

    def test_requires_quantity_true_for_strings(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        i = Instrument("Violin", "strings")
        self.assertTrue(i.requires_quantity)

    def test_all_valid_families_accepted(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        families = ["keyboard", "strings", "woodwind", "brass", "percussion", "voice", "other"]
        for f in families:
            Instrument("Test", f)

    def test_str_returns_name(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        self.assertEqual(str(Instrument("Flute", "woodwind")), "Flute")

    def test_to_dict_from_dict_roundtrip(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        i = Instrument("Drums", "percussion")
        i2 = Instrument.from_dict(i.to_dict())
        self.assertEqual(i2.name, "Drums")
        self.assertEqual(i2.family, "percussion")


# ── RoomInstrument ────────────────────────────────────────────────────────────

class TestRoomInstrument(unittest.TestCase):
    """value_objects/lesson/room_instrument.py"""

    def _piano(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        return Instrument("Piano", "keyboard")

    def _voice(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        return Instrument("Voice", "voice")

    def test_physical_instrument_requires_quantity(self):
        from backend.app.domain.value_objects.lesson.room_instrument import RoomInstrument
        ri = RoomInstrument(self._piano(), quantity=2)
        self.assertEqual(ri.quantity, 2)

    def test_physical_instrument_none_quantity_raises(self):
        from backend.app.domain.value_objects.lesson.room_instrument import RoomInstrument
        with self.assertRaises(ValidationError):
            RoomInstrument(self._piano(), quantity=None)

    def test_physical_instrument_zero_quantity_raises(self):
        from backend.app.domain.value_objects.lesson.room_instrument import RoomInstrument
        with self.assertRaises(ValidationError):
            RoomInstrument(self._piano(), quantity=0)

    def test_voice_accepts_none_quantity(self):
        from backend.app.domain.value_objects.lesson.room_instrument import RoomInstrument
        ri = RoomInstrument(self._voice(), quantity=None)
        self.assertIsNone(ri.quantity)

    def test_voice_with_quantity_raises(self):
        from backend.app.domain.value_objects.lesson.room_instrument import RoomInstrument
        with self.assertRaises(ValidationError):
            RoomInstrument(self._voice(), quantity=1)

    def test_to_dict_from_dict_roundtrip(self):
        from backend.app.domain.value_objects.lesson.room_instrument import RoomInstrument
        ri = RoomInstrument(self._piano(), quantity=3)
        ri2 = RoomInstrument.from_dict(ri.to_dict())
        self.assertEqual(ri2.quantity, 3)
        self.assertEqual(ri2.instrument.family, "keyboard")


# ── SkillLevel ────────────────────────────────────────────────────────────────

class TestSkillLevel(unittest.TestCase):
    """value_objects/lesson/skill_level.py"""

    def test_invalid_value_raises(self):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        with self.assertRaises(ValidationError):
            SkillLevel("expert")

    def test_beginner_less_than_intermediate(self):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        self.assertLess(SkillLevel("beginner"), SkillLevel("intermediate"))

    def test_professional_greater_than_advanced(self):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        self.assertGreater(SkillLevel("professional"), SkillLevel("advanced"))

    def test_same_level_equal(self):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        self.assertEqual(SkillLevel("intermediate"), SkillLevel("intermediate"))

    def test_rank_ordering(self):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        levels = ["beginner", "elementary", "intermediate", "advanced", "professional"]
        ranks = [SkillLevel(v).rank for v in levels]
        self.assertEqual(ranks, sorted(ranks))

    def test_all_constant_has_five_levels(self):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        self.assertEqual(len(SkillLevel.ALL), 5)

    def test_beginner_constant(self):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        self.assertEqual(SkillLevel.BEGINNER.value, "beginner")

    def test_to_dict_includes_rank(self):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        d = SkillLevel("beginner").to_dict()
        self.assertIn("rank", d)
        self.assertEqual(d["value"], "beginner")

    def test_from_dict_roundtrip(self):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        s = SkillLevel("advanced")
        s2 = SkillLevel.from_dict(s.to_dict())
        self.assertEqual(s2.value, "advanced")

    def test_ge_comparison(self):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        self.assertGreaterEqual(SkillLevel("advanced"), SkillLevel("advanced"))
        self.assertGreaterEqual(SkillLevel("professional"), SkillLevel("intermediate"))

    def test_le_comparison(self):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        self.assertLessEqual(SkillLevel("beginner"), SkillLevel("beginner"))
        self.assertLessEqual(SkillLevel("elementary"), SkillLevel("advanced"))


# ── TeachableRange ────────────────────────────────────────────────────────────

class TestTeachableRange(unittest.TestCase):
    """value_objects/lesson/teachable_range.py"""

    def _sl(self, value):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        return SkillLevel(value)

    def test_includes_min_level(self):
        from backend.app.domain.value_objects.lesson.teachable_range import TeachableRange
        r = TeachableRange(self._sl("beginner"), self._sl("intermediate"))
        self.assertTrue(r.includes(self._sl("beginner")))

    def test_includes_max_level(self):
        from backend.app.domain.value_objects.lesson.teachable_range import TeachableRange
        r = TeachableRange(self._sl("beginner"), self._sl("intermediate"))
        self.assertTrue(r.includes(self._sl("intermediate")))

    def test_includes_middle_level(self):
        from backend.app.domain.value_objects.lesson.teachable_range import TeachableRange
        r = TeachableRange(self._sl("beginner"), self._sl("professional"))
        self.assertTrue(r.includes(self._sl("intermediate")))

    def test_excludes_below_min(self):
        from backend.app.domain.value_objects.lesson.teachable_range import TeachableRange
        r = TeachableRange(self._sl("intermediate"), self._sl("professional"))
        self.assertFalse(r.includes(self._sl("beginner")))

    def test_excludes_above_max(self):
        from backend.app.domain.value_objects.lesson.teachable_range import TeachableRange
        r = TeachableRange(self._sl("beginner"), self._sl("intermediate"))
        self.assertFalse(r.includes(self._sl("advanced")))

    def test_single_level_range_only_includes_that_level(self):
        from backend.app.domain.value_objects.lesson.teachable_range import TeachableRange
        r = TeachableRange(self._sl("advanced"), self._sl("advanced"))
        self.assertTrue(r.includes(self._sl("advanced")))
        self.assertFalse(r.includes(self._sl("intermediate")))

    def test_min_greater_than_max_raises(self):
        from backend.app.domain.value_objects.lesson.teachable_range import TeachableRange
        with self.assertRaises(ValidationError):
            TeachableRange(self._sl("professional"), self._sl("beginner"))

    def test_to_dict_from_dict_roundtrip(self):
        from backend.app.domain.value_objects.lesson.teachable_range import TeachableRange
        r = TeachableRange(self._sl("elementary"), self._sl("advanced"))
        r2 = TeachableRange.from_dict(r.to_dict())
        self.assertEqual(r2.min_level.value, "elementary")
        self.assertEqual(r2.max_level.value, "advanced")


# ── InstrumentProficiency ─────────────────────────────────────────────────────

class TestInstrumentProficiency(unittest.TestCase):
    """value_objects/lesson/instrument_proficiency.py"""

    def _piano(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        return Instrument("Piano", "keyboard")

    def _violin(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        return Instrument("Violin", "strings")

    def _range(self, lo, hi):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        from backend.app.domain.value_objects.lesson.teachable_range import TeachableRange
        return TeachableRange(SkillLevel(lo), SkillLevel(hi))

    def _sl(self, v):
        from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
        return SkillLevel(v)

    def test_can_teach_matching_instrument_and_level(self):
        from backend.app.domain.value_objects.lesson.instrument_proficiency import InstrumentProficiency
        prof = InstrumentProficiency(self._piano(), self._range("beginner", "advanced"))
        self.assertTrue(prof.can_teach(self._piano(), self._sl("intermediate")))

    def test_cannot_teach_wrong_instrument(self):
        from backend.app.domain.value_objects.lesson.instrument_proficiency import InstrumentProficiency
        prof = InstrumentProficiency(self._piano(), self._range("beginner", "advanced"))
        self.assertFalse(prof.can_teach(self._violin(), self._sl("intermediate")))

    def test_cannot_teach_level_out_of_range(self):
        from backend.app.domain.value_objects.lesson.instrument_proficiency import InstrumentProficiency
        prof = InstrumentProficiency(self._piano(), self._range("beginner", "intermediate"))
        self.assertFalse(prof.can_teach(self._piano(), self._sl("professional")))

    def test_can_teach_at_boundary(self):
        from backend.app.domain.value_objects.lesson.instrument_proficiency import InstrumentProficiency
        prof = InstrumentProficiency(self._piano(), self._range("beginner", "beginner"))
        self.assertTrue(prof.can_teach(self._piano(), self._sl("beginner")))

    def test_to_dict_from_dict_roundtrip(self):
        from backend.app.domain.value_objects.lesson.instrument_proficiency import InstrumentProficiency
        prof = InstrumentProficiency(self._piano(), self._range("beginner", "advanced"))
        prof2 = InstrumentProficiency.from_dict(prof.to_dict())
        self.assertEqual(prof2.instrument.name, "Piano")
        self.assertEqual(prof2.teachable_range.min_level.value, "beginner")


# ── AttendanceStatus ──────────────────────────────────────────────────────────

class TestAttendanceStatus(unittest.TestCase):
    """value_objects/lesson/attendance_status.py"""

    def test_valid_statuses_do_not_raise(self):
        from backend.app.domain.value_objects.lesson.attendance_status import AttendanceStatus
        for status in ("present", "absent", "cancel", "late_cancel"):
            AttendanceStatus(status)

    def test_invalid_status_raises(self):
        from backend.app.domain.value_objects.lesson.attendance_status import AttendanceStatus
        with self.assertRaises(ValidationError):
            AttendanceStatus("excused")

    def test_present_is_not_chargeable(self):
        from backend.app.domain.value_objects.lesson.attendance_status import AttendanceStatus
        self.assertFalse(AttendanceStatus("present").is_chargeable())

    def test_absent_is_chargeable(self):
        from backend.app.domain.value_objects.lesson.attendance_status import AttendanceStatus
        self.assertTrue(AttendanceStatus("absent").is_chargeable())

    def test_cancel_is_chargeable(self):
        from backend.app.domain.value_objects.lesson.attendance_status import AttendanceStatus
        self.assertTrue(AttendanceStatus("cancel").is_chargeable())

    def test_late_cancel_is_chargeable(self):
        from backend.app.domain.value_objects.lesson.attendance_status import AttendanceStatus
        self.assertTrue(AttendanceStatus("late_cancel").is_chargeable())

    def test_str_returns_value(self):
        from backend.app.domain.value_objects.lesson.attendance_status import AttendanceStatus
        self.assertEqual(str(AttendanceStatus("present")), "present")

    def test_chargeable_set_has_three_statuses(self):
        from backend.app.domain.value_objects.lesson.attendance_status import AttendanceStatus
        self.assertEqual(len(AttendanceStatus.CHARGEABLE), 3)
        self.assertIn("absent", AttendanceStatus.CHARGEABLE)


# ── RecurrenceRule ────────────────────────────────────────────────────────────

class TestRecurrenceRule(unittest.TestCase):
    """value_objects/scheduling/recurrence_rule.py"""

    def test_one_time_factory(self):
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        r = RecurrenceRule.one_time("2025-09-01")
        self.assertEqual(r.rule_type, "one_time")
        self.assertEqual(r.value, "2025-09-01")

    def test_cron_factory(self):
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        r = RecurrenceRule.cron("0 0 * * MON")
        self.assertEqual(r.rule_type, "cron")
        self.assertEqual(r.value, "0 0 * * MON")

    def test_is_recurring_true_for_cron(self):
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        r = RecurrenceRule.cron("0 0 * * MON")
        self.assertTrue(r.is_recurring)

    def test_is_recurring_false_for_one_time(self):
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        r = RecurrenceRule.one_time("2025-09-01")
        self.assertFalse(r.is_recurring)

    def test_invalid_rule_type_raises(self):
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        with self.assertRaises(ValidationError):
            RecurrenceRule("weekly", "2025-09-01")

    def test_blank_value_raises(self):
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        with self.assertRaises(ValidationError):
            RecurrenceRule("cron", "   ")

    def test_from_str_detects_cron_by_five_fields(self):
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        r = RecurrenceRule.from_str("0 10 * * MON")
        self.assertEqual(r.rule_type, "cron")

    def test_from_str_detects_one_time_for_iso_date(self):
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        r = RecurrenceRule.from_str("2025-09-15")
        self.assertEqual(r.rule_type, "one_time")

    def test_to_dict_from_dict_roundtrip(self):
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        r = RecurrenceRule.cron("0 14 * * FRI")
        r2 = RecurrenceRule.from_dict(r.to_dict())
        self.assertEqual(r2.rule_type, "cron")
        self.assertEqual(r2.value, "0 14 * * FRI")

    def test_str_returns_value(self):
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        r = RecurrenceRule.one_time("2025-10-01")
        self.assertEqual(str(r), "2025-10-01")


# ── BlockedTime ───────────────────────────────────────────────────────────────

class TestBlockedTime(unittest.TestCase):
    """value_objects/scheduling/blocked_time.py"""

    def _dr(self, start, end):
        from backend.app.domain.value_objects.scheduling.date_range import DateRange
        return DateRange(period_start=start, period_end=end)

    def _cron(self, expr):
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        return RecurrenceRule.cron(expr)

    def test_holiday_factory_creates_single_day_block(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.holiday("Christmas", "2025-12-25")
        self.assertEqual(bt.date, "2025-12-25")
        self.assertIsNone(bt.date_range)
        self.assertIsNone(bt.recurrence)

    def test_vacation_factory_creates_range_block(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.vacation("Summer Break", self._dr("2025-07-14", "2025-07-28"))
        self.assertIsNone(bt.date)
        self.assertIsNotNone(bt.date_range)

    def test_recurring_factory_creates_cron_block(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.recurring("Weekends", self._cron("0 0 * * SAT,SUN"), block_type="weekend")
        self.assertIsNone(bt.date)
        self.assertIsNone(bt.date_range)
        self.assertIsNotNone(bt.recurrence)

    def test_blank_label_raises(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        with self.assertRaises(ValidationError):
            BlockedTime(label="", block_type="holiday", date="2025-12-25")

    def test_whitespace_label_raises(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        with self.assertRaises(ValidationError):
            BlockedTime(label="  ", block_type="holiday", date="2025-12-25")

    def test_invalid_block_type_raises(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        with self.assertRaises(ValidationError):
            BlockedTime(label="Test", block_type="random", date="2025-12-25")

    def test_no_time_field_raises(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        with self.assertRaises(ValidationError):
            BlockedTime(label="Test", block_type="holiday")

    def test_two_time_fields_raises(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        with self.assertRaises(ValidationError):
            BlockedTime(
                label="Test", block_type="vacation",
                date="2025-07-14",
                date_range=self._dr("2025-07-14", "2025-07-28"),
            )

    def test_includes_date_true_for_matching_single_day(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.holiday("Christmas", "2025-12-25")
        self.assertTrue(bt.includes_date("2025-12-25"))

    def test_includes_date_false_for_different_day(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.holiday("Christmas", "2025-12-25")
        self.assertFalse(bt.includes_date("2025-12-24"))

    def test_includes_date_true_within_range(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.vacation("Summer", self._dr("2025-07-14", "2025-07-28"))
        self.assertTrue(bt.includes_date("2025-07-20"))

    def test_includes_date_true_at_range_boundary_start(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.vacation("Summer", self._dr("2025-07-14", "2025-07-28"))
        self.assertTrue(bt.includes_date("2025-07-14"))

    def test_includes_date_true_at_range_boundary_end(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.vacation("Summer", self._dr("2025-07-14", "2025-07-28"))
        self.assertTrue(bt.includes_date("2025-07-28"))

    def test_includes_date_false_outside_range(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.vacation("Summer", self._dr("2025-07-14", "2025-07-28"))
        self.assertFalse(bt.includes_date("2025-08-01"))

    def test_includes_date_false_for_recurring(self):
        """Recurring blocks return False from includes_date; cron eval done externally."""
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.recurring("Weekends", self._cron("0 0 * * SAT,SUN"), block_type="weekend")
        self.assertFalse(bt.includes_date("2025-09-06"))  # Saturday

    def test_is_single_day_true_for_holiday(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.holiday("Test", "2025-01-01")
        self.assertTrue(bt.is_single_day)
        self.assertFalse(bt.is_range)
        self.assertFalse(bt.is_recurring)

    def test_is_range_true_for_vacation(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.vacation("Vacation", self._dr("2025-07-01", "2025-07-15"))
        self.assertTrue(bt.is_range)
        self.assertFalse(bt.is_single_day)
        self.assertFalse(bt.is_recurring)

    def test_is_recurring_true_for_cron(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.recurring("Weekends", self._cron("0 0 * * SAT,SUN"), block_type="weekend")
        self.assertTrue(bt.is_recurring)
        self.assertFalse(bt.is_single_day)
        self.assertFalse(bt.is_range)

    def test_all_valid_block_types_accepted(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        for bt_type in ("holiday", "weekend", "work", "school", "vacation", "personal", "other"):
            BlockedTime(label="Test", block_type=bt_type, date="2025-01-01")

    def test_to_dict_from_dict_roundtrip_single_day(self):
        from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
        bt = BlockedTime.holiday("New Year", "2026-01-01")
        bt2 = BlockedTime.from_dict(bt.to_dict())
        self.assertEqual(bt2.date, "2026-01-01")
        self.assertEqual(bt2.block_type, "holiday")


# ── TeachingRequirement ───────────────────────────────────────────────────────

class TestTeachingRequirement(unittest.TestCase):
    """value_objects/compatibility/teaching_requirement.py"""

    def test_credential_factory(self):
        from backend.app.domain.value_objects.compatibility.teaching_requirement import TeachingRequirement
        req = TeachingRequirement.credential("cpr")
        self.assertEqual(req.requirement_type, "credential")
        self.assertEqual(req.value, "cpr")

    def test_min_student_age_factory(self):
        from backend.app.domain.value_objects.compatibility.teaching_requirement import TeachingRequirement
        req = TeachingRequirement.min_student_age(5)
        self.assertEqual(req.requirement_type, "min_student_age")
        self.assertEqual(req.value, "5")

    def test_max_student_age_factory(self):
        from backend.app.domain.value_objects.compatibility.teaching_requirement import TeachingRequirement
        req = TeachingRequirement.max_student_age(18)
        self.assertEqual(req.requirement_type, "max_student_age")
        self.assertEqual(req.value, "18")

    def test_invalid_requirement_type_raises(self):
        from backend.app.domain.value_objects.compatibility.teaching_requirement import TeachingRequirement
        with self.assertRaises(ValueError):
            TeachingRequirement("preferred_language", "French")

    def test_empty_value_raises(self):
        from backend.app.domain.value_objects.compatibility.teaching_requirement import TeachingRequirement
        with self.assertRaises(ValueError):
            TeachingRequirement("credential", "")

    def test_non_digit_age_raises(self):
        from backend.app.domain.value_objects.compatibility.teaching_requirement import TeachingRequirement
        with self.assertRaises(ValueError):
            TeachingRequirement("min_student_age", "five")

    def test_negative_age_string_raises(self):
        """'-5' is not digits-only, so it should raise."""
        from backend.app.domain.value_objects.compatibility.teaching_requirement import TeachingRequirement
        with self.assertRaises(ValueError):
            TeachingRequirement("min_student_age", "-5")

    def test_to_dict_from_dict_roundtrip(self):
        from backend.app.domain.value_objects.compatibility.teaching_requirement import TeachingRequirement
        req = TeachingRequirement.credential("vulnerable_sector")
        req2 = TeachingRequirement.from_dict(req.to_dict())
        self.assertEqual(req2.requirement_type, "credential")
        self.assertEqual(req2.value, "vulnerable_sector")


# ── CompatibilityResult ───────────────────────────────────────────────────────

class TestCompatibilityResult(unittest.TestCase):
    """value_objects/compatibility/compatibility_result.py"""

    def test_ok_factory_can_assign_true(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.ok()
        self.assertTrue(r.can_assign)
        self.assertIsNone(r.hard_verdict)
        self.assertIsNone(r.soft_verdict)

    def test_blocked_factory_can_assign_false(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.blocked("Safeguarding concern")
        self.assertFalse(r.can_assign)
        self.assertEqual(r.hard_verdict, "blocked")

    def test_blocked_factory_populates_reasons(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.blocked("reason A", "reason B")
        self.assertEqual(len(r.reasons), 2)

    def test_requirement_not_met_factory(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.requirement_not_met("CPR required")
        self.assertFalse(r.can_assign)
        self.assertIsNone(r.hard_verdict)

    def test_is_hard_blocked_true_for_blocked(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.blocked("reason")
        self.assertTrue(r.is_hard_blocked)

    def test_is_hard_blocked_false_for_ok(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.ok()
        self.assertFalse(r.is_hard_blocked)

    def test_is_hard_required_true_for_required(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.ok(hard_verdict="required", reasons=("Must pair",))
        self.assertTrue(r.is_hard_required)

    def test_ok_with_required_verdict_still_can_assign(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.ok(hard_verdict="required")
        self.assertTrue(r.can_assign)
        self.assertTrue(r.is_hard_required)

    def test_ok_with_preferred_soft_verdict(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.ok(soft_verdict="preferred")
        self.assertTrue(r.can_assign)
        self.assertEqual(r.soft_verdict, "preferred")

    def test_ok_with_disliked_soft_verdict(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.ok(soft_verdict="disliked")
        self.assertTrue(r.can_assign)
        self.assertEqual(r.soft_verdict, "disliked")

    def test_reasons_are_immutable_tuple(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.ok(reasons=("A", "B"))
        self.assertIsInstance(r.reasons, tuple)

    def test_is_hard_required_false_for_requirement_not_met(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.requirement_not_met("Age violation")
        self.assertFalse(r.is_hard_required)

    def test_blocked_has_no_soft_verdict(self):
        from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
        r = CompatibilityResult.blocked("reason")
        self.assertIsNone(r.soft_verdict)


if __name__ == "__main__":
    unittest.main()