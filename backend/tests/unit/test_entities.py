"""
Unit tests for domain entities with non-trivial business logic.

Covers:
  CredentialEntity           — is_expired, can_teach
  InstructorStudentCompatibilityEntity — validation, from_dict
  CourseEntity               — validation, lead_instructor_id, is_full, accepts_skill_level
  StudentEntity              — from_dict round-trip
  InstructorEntity           — from_dict round-trip
  LessonEntity               — from_dict round-trip
  LessonOccurrenceEntity     — default status, from_dict
"""
import unittest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _instrument(name="Piano", family="keyboard"):
    from backend.app.domain.value_objects.lesson.instrument import Instrument
    return Instrument(name, family)


def _sl(value):
    from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
    return SkillLevel(value)


def _range(lo, hi):
    from backend.app.domain.value_objects.lesson.teachable_range import TeachableRange
    return TeachableRange(_sl(lo), _sl(hi))


def _proficiency(instrument=None, lo="beginner", hi="professional"):
    from backend.app.domain.value_objects.lesson.instrument_proficiency import InstrumentProficiency
    return InstrumentProficiency(instrument or _instrument(), _range(lo, hi))


def _date_range(start, end):
    from backend.app.domain.value_objects.scheduling.date_range import DateRange
    return DateRange(period_start=start, period_end=end)


# ── CredentialEntity ──────────────────────────────────────────────────────────

class TestCredentialEntity(unittest.TestCase):
    """domain/entities/credential.py"""

    def _cred(self, instructor_id="i1", credential_type="musical",
              valid_from=None, valid_until=None, proficiencies=None):
        from backend.app.domain.entities.credential import CredentialEntity
        from backend.app.domain.value_objects.scheduling.date_range import DateRange
        return CredentialEntity(
            credential_id="cred-1",
            instructor_id=instructor_id,
            proficiencies=proficiencies or [],
            credential_type=credential_type,
            validity=DateRange(valid_from, valid_until) if valid_from and valid_until else None,
        )

    def test_is_expired_false_when_no_validity(self):
        c = self._cred()
        self.assertFalse(c.is_expired)

    def test_is_expired_false_when_validity_in_future(self):
        """Today is 2026-03-29; a credential valid until 2026-12-31 is not expired."""
        c = self._cred(valid_from="2026-01-01", valid_until="2026-12-31")
        self.assertFalse(c.is_expired)

    def test_is_expired_true_when_validity_in_past(self):
        """A credential that ended 2025-12-31 is expired today (2026-03-29)."""
        c = self._cred(valid_from="2025-01-01", valid_until="2025-12-31")
        self.assertTrue(c.is_expired)

    def test_is_expired_uses_period_end(self):
        """Exactly the last day of validity is still active (not expired)."""
        c = self._cred(valid_from="2026-01-01", valid_until="2026-03-29")
        self.assertFalse(c.is_expired)

    def test_can_teach_true_when_proficiency_matches(self):
        prof = _proficiency(_instrument("Piano", "keyboard"), "beginner", "advanced")
        c = self._cred(proficiencies=[prof])
        self.assertTrue(c.can_teach(_instrument("Piano", "keyboard"), _sl("intermediate")))

    def test_can_teach_false_when_no_proficiency(self):
        c = self._cred(proficiencies=[])
        self.assertFalse(c.can_teach(_instrument("Piano", "keyboard"), _sl("intermediate")))

    def test_can_teach_false_for_wrong_instrument(self):
        from backend.app.domain.value_objects.lesson.instrument import Instrument
        prof = _proficiency(_instrument("Piano", "keyboard"), "beginner", "advanced")
        c = self._cred(proficiencies=[prof])
        self.assertFalse(c.can_teach(Instrument("Violin", "strings"), _sl("intermediate")))

    def test_from_dict_parses_validity(self):
        from backend.app.domain.entities.credential import CredentialEntity
        row = {
            "credential_id": "c1",
            "instructor_id": "i1",
            "proficiencies": [],
            "credential_type": "cpr",
            "valid_from": "2024-01-01",
            "valid_until": "2026-12-31",
        }
        c = CredentialEntity.from_dict(row)
        self.assertIsNotNone(c.validity)
        self.assertEqual(c.validity.period_start, "2024-01-01")

    def test_from_dict_without_validity(self):
        from backend.app.domain.entities.credential import CredentialEntity
        row = {
            "credential_id": "c1",
            "instructor_id": "i1",
            "proficiencies": [],
        }
        c = CredentialEntity.from_dict(row)
        self.assertIsNone(c.validity)

    def test_to_dict_includes_credential_type(self):
        c = self._cred(credential_type="special_ed")
        d = c.to_dict()
        self.assertEqual(d["credential_type"], "special_ed")

    def test_all_valid_credential_types_accepted(self):
        from backend.app.domain.entities.credential import CredentialEntity, VALID_CREDENTIAL_TYPES
        for ct in VALID_CREDENTIAL_TYPES:
            CredentialEntity(
                credential_id="c1",
                instructor_id="i1",
                proficiencies=[],
                credential_type=ct,
            )


# ── InstructorStudentCompatibilityEntity ──────────────────────────────────────

class TestInstructorStudentCompatibilityEntity(unittest.TestCase):
    """domain/entities/instructor_student_compatibility.py"""

    def _entity(self, verdict="blocked", initiated_by="admin"):
        from backend.app.domain.entities.instructor_student_compatibility import (
            InstructorStudentCompatibilityEntity,
        )
        return InstructorStudentCompatibilityEntity(
            compatibility_id="c1",
            instructor_id="i1",
            student_id="s1",
            verdict=verdict,
            reason="test reason",
            initiated_by=initiated_by,
        )

    def test_all_valid_verdicts_accepted(self):
        for verdict in ("blocked", "required", "preferred", "disliked"):
            self._entity(verdict=verdict)

    def test_invalid_verdict_raises(self):
        with self.assertRaises(ValueError):
            self._entity(verdict="allowed")

    def test_all_valid_initiators_accepted(self):
        for initiator in ("student", "instructor", "admin"):
            self._entity(initiated_by=initiator)

    def test_invalid_initiator_raises(self):
        with self.assertRaises(ValueError):
            self._entity(initiated_by="system")

    def test_from_dict_roundtrip(self):
        from backend.app.domain.entities.instructor_student_compatibility import (
            InstructorStudentCompatibilityEntity,
        )
        row = {
            "compatibility_id": "c1",
            "instructor_id": "i1",
            "student_id": "s1",
            "verdict": "preferred",
            "reason": "student request",
            "initiated_by": "student",
        }
        entity = InstructorStudentCompatibilityEntity.from_dict(row)
        self.assertEqual(entity.verdict, "preferred")
        self.assertEqual(entity.initiated_by, "student")

    def test_from_dict_reason_defaults_to_empty_string(self):
        from backend.app.domain.entities.instructor_student_compatibility import (
            InstructorStudentCompatibilityEntity,
        )
        row = {
            "compatibility_id": "c1",
            "instructor_id": "i1",
            "student_id": "s1",
            "verdict": "disliked",
            "initiated_by": "admin",
        }
        entity = InstructorStudentCompatibilityEntity.from_dict(row)
        self.assertEqual(entity.reason, "")

    def test_to_dict_includes_all_fields(self):
        entity = self._entity(verdict="required", initiated_by="instructor")
        d = entity.to_dict()
        self.assertIn("compatibility_id", d)
        self.assertIn("instructor_id", d)
        self.assertIn("student_id", d)
        self.assertIn("verdict", d)
        self.assertIn("reason", d)
        self.assertIn("initiated_by", d)


# ── CourseEntity ──────────────────────────────────────────────────────────────

class TestCourseEntity(unittest.TestCase):
    """domain/entities/course.py"""

    def _course(self, instructor_ids=None, student_ids=None, capacity=None,
                status="draft", skill_range=None):
        from backend.app.domain.entities.course import CourseEntity
        from backend.app.domain.value_objects.scheduling.date_range import DateRange
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        from backend.app.domain.value_objects.scheduling.time_slot import TimeSlot
        return CourseEntity(
            course_id="c1",
            name="Test Course",
            room_id="r1",
            instructor_ids=instructor_ids or ["i1"],
            student_ids=student_ids or [],
            period=DateRange("2025-09-01", "2025-12-31"),
            recurrence=RecurrenceRule.cron("0 10 * * MON"),
            time_slot=TimeSlot("10:00:00", "11:00:00"),
            capacity=capacity,
            skill_range=skill_range,
            status=status,
        )

    def test_lead_instructor_id_is_first(self):
        c = self._course(instructor_ids=["i1", "i2"])
        self.assertEqual(c.lead_instructor_id, "i1")

    def test_is_full_false_when_no_capacity(self):
        c = self._course(capacity=None, student_ids=["s1", "s2"])
        self.assertFalse(c.is_full)

    def test_is_full_false_below_capacity(self):
        c = self._course(capacity=5, student_ids=["s1", "s2"])
        self.assertFalse(c.is_full)

    def test_is_full_true_at_capacity(self):
        c = self._course(capacity=2, student_ids=["s1", "s2"])
        self.assertTrue(c.is_full)

    def test_is_full_true_when_over_capacity(self):
        """Safety check: even if somehow over capacity."""
        c = self._course(capacity=1, student_ids=["s1", "s2"])
        self.assertTrue(c.is_full)

    def test_accepts_skill_level_true_when_no_range(self):
        c = self._course(skill_range=None)
        self.assertTrue(c.accepts_skill_level(_sl("professional")))

    def test_accepts_skill_level_true_when_in_range(self):
        c = self._course(skill_range=_range("beginner", "intermediate"))
        self.assertTrue(c.accepts_skill_level(_sl("intermediate")))

    def test_accepts_skill_level_false_when_out_of_range(self):
        c = self._course(skill_range=_range("beginner", "intermediate"))
        self.assertFalse(c.accepts_skill_level(_sl("advanced")))

    def test_invalid_status_raises(self):
        with self.assertRaises(ValueError):
            self._course(status="running")

    def test_all_valid_statuses_accepted(self):
        for status in ("draft", "active", "completed", "cancelled"):
            self._course(status=status)

    def test_empty_instructor_ids_raises(self):
        from backend.app.domain.entities.course import CourseEntity
        from backend.app.domain.value_objects.scheduling.date_range import DateRange
        from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
        from backend.app.domain.value_objects.scheduling.time_slot import TimeSlot
        with self.assertRaises(ValueError):
            CourseEntity(
                course_id="c1",
                name="Test",
                room_id="r1",
                instructor_ids=[],   # explicitly empty — should raise
                student_ids=[],
                period=DateRange("2025-09-01", "2025-12-31"),
                recurrence=RecurrenceRule.cron("0 10 * * MON"),
                time_slot=TimeSlot("10:00:00", "11:00:00"),
            )

    def test_to_dict_includes_expected_keys(self):
        c = self._course()
        d = c.to_dict()
        for key in ("course_id", "name", "room_id", "instructor_ids", "student_ids",
                    "period_start", "period_end", "recurrence", "start_time", "end_time"):
            self.assertIn(key, d)

    def test_from_dict_roundtrip(self):
        from backend.app.domain.entities.course import CourseEntity
        c = self._course(instructor_ids=["i1", "i2"], student_ids=["s1"], capacity=10)
        c2 = CourseEntity.from_dict(c.to_dict())
        self.assertEqual(c2.lead_instructor_id, "i1")
        self.assertEqual(len(c2.student_ids), 1)
        self.assertEqual(c2.capacity, 10)

    def test_from_dict_default_status_is_draft(self):
        from backend.app.domain.entities.course import CourseEntity
        c = self._course()
        d = c.to_dict()
        d.pop("status", None)
        c2 = CourseEntity.from_dict(d)
        self.assertEqual(c2.status, "draft")


# ── StudentEntity ─────────────────────────────────────────────────────────────

class TestStudentEntity(unittest.TestCase):
    """domain/entities/student.py"""

    def test_from_dict_minimal_row(self):
        from backend.app.domain.entities.student import StudentEntity
        row = {"student_id": "s1", "person_id": "p1"}
        s = StudentEntity.from_dict(row)
        self.assertEqual(s.student_id, "s1")
        self.assertIsNone(s.age)
        self.assertEqual(s.instrument_skill_levels, [])
        self.assertEqual(s.requirements, [])

    def test_from_dict_with_instrument_skill_levels(self):
        from backend.app.domain.entities.student import StudentEntity
        row = {
            "student_id": "s1",
            "person_id": "p1",
            "instrument_skill_levels": [
                {"name": "Piano", "family": "keyboard", "skill_level": "advanced"},
                {"name": "Voice", "family": "voice", "skill_level": "beginner"},
            ],
        }
        s = StudentEntity.from_dict(row)
        self.assertEqual(len(s.instrument_skill_levels), 2)
        self.assertEqual(s.instrument_skill_levels[0].instrument.name, "Piano")
        self.assertEqual(s.instrument_skill_levels[0].skill_level.value, "advanced")

    def test_skill_level_for(self):
        from backend.app.domain.entities.student import StudentEntity
        row = {
            "student_id": "s1",
            "person_id": "p1",
            "instrument_skill_levels": [
                {"name": "Piano", "family": "keyboard", "skill_level": "intermediate"},
            ],
        }
        s = StudentEntity.from_dict(row)
        self.assertEqual(s.skill_level_for("Piano", "keyboard").value, "intermediate")
        self.assertIsNone(s.skill_level_for("Guitar", "strings"))

    def test_from_dict_with_requirements(self):
        from backend.app.domain.entities.student import StudentEntity
        row = {
            "student_id": "s1",
            "person_id": "p1",
            "requirements": [
                {"requirement_type": "credential", "value": "cpr"}
            ],
        }
        s = StudentEntity.from_dict(row)
        self.assertEqual(len(s.requirements), 1)
        self.assertEqual(s.requirements[0].value, "cpr")

    def test_to_dict_roundtrip(self):
        from backend.app.domain.entities.student import StudentEntity
        row = {
            "student_id": "s1",
            "person_id": "p1",
            "instrument_skill_levels": [
                {"name": "Piano", "family": "keyboard", "skill_level": "intermediate"},
            ],
            "age": 14,
            "client_id": "c1",
            "requirements": [],
        }
        s = StudentEntity.from_dict(row)
        d = s.to_dict()
        self.assertEqual(len(d["instrument_skill_levels"]), 1)
        self.assertEqual(d["instrument_skill_levels"][0]["skill_level"], "intermediate")
        self.assertEqual(d["age"], 14)
        self.assertEqual(d["client_id"], "c1")


# ── InstructorEntity ──────────────────────────────────────────────────────────

class TestInstructorEntity(unittest.TestCase):
    """domain/entities/instructor.py"""

    def test_from_dict_minimal_row(self):
        from backend.app.domain.entities.instructor import InstructorEntity
        row = {"instructor_id": "i1", "person_id": "p1"}
        inst = InstructorEntity.from_dict(row)
        self.assertEqual(inst.instructor_id, "i1")
        self.assertIsNone(inst.hourly_rate)
        self.assertEqual(inst.blocked_times, [])
        self.assertEqual(inst.restrictions, [])

    def test_from_dict_with_hourly_rate(self):
        from backend.app.domain.entities.instructor import InstructorEntity
        row = {"instructor_id": "i1", "person_id": "p1", "hourly_rate": 65.0}
        inst = InstructorEntity.from_dict(row)
        self.assertIsNotNone(inst.hourly_rate)
        self.assertAlmostEqual(inst.hourly_rate.amount.amount, 65.0)

    def test_from_dict_with_restrictions(self):
        from backend.app.domain.entities.instructor import InstructorEntity
        row = {
            "instructor_id": "i1",
            "person_id": "p1",
            "restrictions": [
                {"requirement_type": "min_student_age", "value": "8"}
            ],
        }
        inst = InstructorEntity.from_dict(row)
        self.assertEqual(len(inst.restrictions), 1)
        self.assertEqual(inst.restrictions[0].value, "8")

    def test_to_dict_includes_instructor_id(self):
        from backend.app.domain.entities.instructor import InstructorEntity
        inst = InstructorEntity(instructor_id="i1", person_id="p1")
        d = inst.to_dict()
        self.assertIn("instructor_id", d)
        self.assertIn("person_id", d)


# ── LessonEntity ──────────────────────────────────────────────────────────────

class TestLessonEntity(unittest.TestCase):
    """domain/entities/lesson.py"""

    def test_from_dict_with_one_time_recurrence(self):
        from backend.app.domain.entities.lesson import LessonEntity
        row = {
            "lesson_id": "l1",
            "instructor_id": "i1",
            "room_id": "r1",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "recurrence": "2025-09-01",
        }
        lesson = LessonEntity.from_dict(row)
        self.assertEqual(lesson.recurrence.rule_type, "one_time")

    def test_from_dict_with_cron_recurrence(self):
        from backend.app.domain.entities.lesson import LessonEntity
        row = {
            "lesson_id": "l1",
            "instructor_id": "i1",
            "room_id": "r1",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "recurrence": "0 10 * * MON",
        }
        lesson = LessonEntity.from_dict(row)
        self.assertEqual(lesson.recurrence.rule_type, "cron")

    def test_from_dict_without_recurrence(self):
        from backend.app.domain.entities.lesson import LessonEntity
        row = {
            "lesson_id": "l1",
            "instructor_id": "i1",
            "room_id": "r1",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
        }
        lesson = LessonEntity.from_dict(row)
        self.assertIsNone(lesson.recurrence)

    def test_from_dict_with_rate(self):
        from backend.app.domain.entities.lesson import LessonEntity
        row = {
            "lesson_id": "l1",
            "instructor_id": "i1",
            "room_id": "r1",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "rate": 50.0,
        }
        lesson = LessonEntity.from_dict(row)
        self.assertIsNotNone(lesson.rate)
        self.assertAlmostEqual(lesson.rate.amount.amount, 50.0)

    def test_to_dict_roundtrip(self):
        from backend.app.domain.entities.lesson import LessonEntity
        from backend.app.domain.value_objects.scheduling.time_slot import TimeSlot
        lesson = LessonEntity(
            lesson_id="l1",
            instructor_id="i1",
            room_id="r1",
            time_slot=TimeSlot("10:00:00", "11:00:00"),
        )
        d = lesson.to_dict()
        self.assertEqual(d["lesson_id"], "l1")
        self.assertEqual(d["start_time"], "10:00:00")


# ── LessonOccurrenceEntity ────────────────────────────────────────────────────

class TestLessonOccurrenceEntity(unittest.TestCase):
    """domain/entities/lesson_occurrence.py"""

    def _occurrence(self, status=None):
        from backend.app.domain.entities.lesson_occurrence import LessonOccurrenceEntity
        from backend.app.domain.value_objects.scheduling.time_slot import TimeSlot
        kwargs = dict(
            occurrence_id="occ-1",
            date="2025-09-01",
            time_slot=TimeSlot("10:00:00", "11:00:00"),
            instructor_id="i1",
            room_id="r1",
        )
        if status is not None:
            from backend.app.domain.value_objects.scheduling.lesson_status import LessonStatus
            kwargs["status"] = LessonStatus(status)
        return LessonOccurrenceEntity(**kwargs)

    def test_default_status_is_scheduled(self):
        occ = self._occurrence()
        self.assertEqual(occ.status.value, "Scheduled")

    def test_completed_status_accepted(self):
        occ = self._occurrence(status="Completed")
        self.assertEqual(occ.status.value, "Completed")

    def test_from_dict_parses_status(self):
        from backend.app.domain.entities.lesson_occurrence import LessonOccurrenceEntity
        row = {
            "occurrence_id": "occ-1",
            "date": "2025-09-01",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "instructor_id": "i1",
            "room_id": "r1",
            "status": "Completed",
        }
        occ = LessonOccurrenceEntity.from_dict(row)
        self.assertEqual(occ.status.value, "Completed")

    def test_from_dict_default_status_is_scheduled(self):
        from backend.app.domain.entities.lesson_occurrence import LessonOccurrenceEntity
        row = {
            "occurrence_id": "occ-1",
            "date": "2025-09-01",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "instructor_id": "i1",
            "room_id": "r1",
        }
        occ = LessonOccurrenceEntity.from_dict(row)
        self.assertEqual(occ.status.value, "Scheduled")

    def test_to_dict_includes_expected_keys(self):
        occ = self._occurrence()
        d = occ.to_dict()
        for key in ("occurrence_id", "date", "start_time", "end_time",
                    "instructor_id", "room_id", "status"):
            self.assertIn(key, d)

    def test_is_rescheduled_defaults_false(self):
        occ = self._occurrence()
        self.assertFalse(occ.is_rescheduled)


if __name__ == "__main__":
    unittest.main()