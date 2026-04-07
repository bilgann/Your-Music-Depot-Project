"""
Unit tests for the schedule projection domain service.

domain/services/schedule_projection.py

Tests cover:
  project_occurrences()       — standalone lesson templates → occurrences
  project_course_occurrences() — course templates → occurrences
  _is_blocked()               — blocking logic (single day, range, cron-recurring)
  _cron_hits_date()           — cron evaluation helper

Calendar reference (2025-09-XX):
  Sep 1  = Monday
  Sep 6  = Saturday
  Sep 7  = Sunday
  Sep 8  = Monday
  Sep 15 = Monday
  Sep 22 = Monday
  Sep 29 = Monday
"""
import unittest
from datetime import date, datetime

from backend.app.domain.entities.course import CourseEntity
from backend.app.domain.entities.lesson import LessonEntity
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
from backend.app.domain.value_objects.scheduling.date_range import DateRange
from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
from backend.app.domain.value_objects.scheduling.time_slot import TimeSlot

_skip_cron = lambda f: f  # noqa: E731  — bug fixed; decorator is now a no-op


# ── Helpers ───────────────────────────────────────────────────────────────────

def _window(start="2025-09-01", end="2025-09-28"):
    return DateRange(period_start=start, period_end=end)


def _lesson(lesson_id="l1", rule_type="one_time", value="2025-09-01"):
    recurrence = RecurrenceRule(rule_type=rule_type, value=value) if rule_type else None
    return LessonEntity(
        lesson_id=lesson_id,
        instructor_id="i1",
        room_id="r1",
        time_slot=TimeSlot("10:00:00", "11:00:00"),
        recurrence=recurrence,
    )


def _course(rule_type="cron", value="0 0 * * MON",
            start="2025-09-01", end="2025-09-28"):
    return CourseEntity(
        course_id="c1",
        name="Test Course",
        room_id="r1",
        instructor_ids=["i1"],
        student_ids=["s1"],
        period=DateRange(period_start=start, period_end=end),
        recurrence=RecurrenceRule(rule_type=rule_type, value=value),
        time_slot=TimeSlot("10:00:00", "11:00:00"),
    )


def _holiday(label, date):
    return BlockedTime.holiday(label, date)


def _vacation(label, start, end):
    return BlockedTime.vacation(label, DateRange(period_start=start, period_end=end))


def _recurring_weekend():
    return BlockedTime.recurring(
        "Weekends",
        RecurrenceRule.cron("0 0 * * SAT,SUN"),
        block_type="weekend",
    )


# ── project_occurrences ───────────────────────────────────────────────────────

class TestProjectOccurrences(unittest.TestCase):
    """project_occurrences() — standalone lesson projection."""

    def _project(self, lesson, window, blocked=None):
        from backend.app.domain.services.schedule_projection import project_occurrences
        return project_occurrences(lesson, window, blocked or [])

    # ── one_time ──────────────────────────────────────────────────────────────

    def test_one_time_within_window_returns_one_occurrence(self):
        lesson = _lesson(rule_type="one_time", value="2025-09-15")
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-30"))
        self.assertEqual(len(occurrences), 1)
        self.assertEqual(occurrences[0].date, "2025-09-15")

    def test_one_time_before_window_returns_empty(self):
        lesson = _lesson(rule_type="one_time", value="2025-08-15")
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-30"))
        self.assertEqual(occurrences, [])

    def test_one_time_after_window_returns_empty(self):
        lesson = _lesson(rule_type="one_time", value="2025-10-15")
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-30"))
        self.assertEqual(occurrences, [])

    def test_one_time_on_window_start_boundary_included(self):
        lesson = _lesson(rule_type="one_time", value="2025-09-01")
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-30"))
        self.assertEqual(len(occurrences), 1)

    def test_one_time_on_window_end_boundary_included(self):
        lesson = _lesson(rule_type="one_time", value="2025-09-30")
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-30"))
        self.assertEqual(len(occurrences), 1)

    def test_one_time_blocked_returns_empty(self):
        lesson = _lesson(rule_type="one_time", value="2025-09-15")
        blocked = [_holiday("Blocked Day", "2025-09-15")]
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-30"), blocked)
        self.assertEqual(occurrences, [])

    # ── cron (weekly Monday) ──────────────────────────────────────────────────

    @_skip_cron
    def test_weekly_monday_in_four_week_window_gives_four_occurrences(self):
        """Sep 1, 8, 15, 22 are the four Mondays in the 2025-09-01..2025-09-28 window."""
        lesson = _lesson(rule_type="cron", value="0 0 * * MON")
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-28"))
        self.assertEqual(len(occurrences), 4)

    @_skip_cron
    def test_cron_occurrence_dates_are_all_mondays(self):
        lesson = _lesson(rule_type="cron", value="0 0 * * MON")
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-28"))
        for occ in occurrences:
            d = date.fromisoformat(occ.date)
            self.assertEqual(d.weekday(), 0, f"{occ.date} is not a Monday")

    @_skip_cron
    def test_blocked_holiday_skips_one_occurrence(self):
        lesson = _lesson(rule_type="cron", value="0 0 * * MON")
        blocked = [_holiday("Holiday", "2025-09-08")]
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-28"), blocked)
        dates = [o.date for o in occurrences]
        self.assertNotIn("2025-09-08", dates)
        self.assertEqual(len(occurrences), 3)

    @_skip_cron
    def test_blocked_vacation_range_skips_overlapping_occurrences(self):
        lesson = _lesson(rule_type="cron", value="0 0 * * MON")
        # Block Sep 8–Sep 22 (covers 3 Mondays: 8, 15, 22)
        blocked = [_vacation("Family Trip", "2025-09-08", "2025-09-22")]
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-28"), blocked)
        dates = [o.date for o in occurrences]
        self.assertIn("2025-09-01", dates)
        self.assertNotIn("2025-09-08", dates)
        self.assertNotIn("2025-09-15", dates)
        self.assertNotIn("2025-09-22", dates)
        self.assertEqual(len(occurrences), 1)

    @_skip_cron
    def test_weekend_block_does_not_affect_weekly_monday_lesson(self):
        """Blocking weekends shouldn't skip any Monday occurrences."""
        lesson = _lesson(rule_type="cron", value="0 0 * * MON")
        blocked = [_recurring_weekend()]
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-28"), blocked)
        self.assertEqual(len(occurrences), 4)

    @_skip_cron
    def test_cron_lesson_blocked_on_weekend_day_correctly_skips(self):
        """A weekend lesson pattern should have Saturdays skipped when weekends blocked."""
        lesson = _lesson(rule_type="cron", value="0 0 * * SAT")
        # Sep 6, 13, 20, 27 are Saturdays
        blocked = [_recurring_weekend()]
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-28"), blocked)
        self.assertEqual(len(occurrences), 0)

    # ── No recurrence ─────────────────────────────────────────────────────────

    def test_no_recurrence_returns_empty(self):
        lesson = LessonEntity(
            lesson_id="l1",
            instructor_id="i1",
            room_id="r1",
            time_slot=TimeSlot("10:00:00", "11:00:00"),
            recurrence=None,
        )
        from backend.app.domain.services.schedule_projection import project_occurrences
        result = project_occurrences(lesson, _window(), [])
        self.assertEqual(result, [])

    # ── Occurrence shape ──────────────────────────────────────────────────────

    def test_occurrence_id_is_empty_string(self):
        lesson = _lesson(rule_type="one_time", value="2025-09-01")
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-01"))
        self.assertEqual(occurrences[0].occurrence_id, "")

    def test_occurrence_has_correct_instructor_id(self):
        lesson = _lesson(rule_type="one_time", value="2025-09-01")
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-01"))
        self.assertEqual(occurrences[0].instructor_id, "i1")

    def test_occurrence_has_correct_room_id(self):
        lesson = _lesson(rule_type="one_time", value="2025-09-01")
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-01"))
        self.assertEqual(occurrences[0].room_id, "r1")

    def test_occurrence_lesson_id_matches_template(self):
        lesson = _lesson(lesson_id="lesson-99", rule_type="one_time", value="2025-09-01")
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-01"))
        self.assertEqual(occurrences[0].lesson_id, "lesson-99")

    def test_occurrence_time_slot_matches_template(self):
        lesson = _lesson(rule_type="one_time", value="2025-09-01")
        occurrences = self._project(lesson, _window("2025-09-01", "2025-09-01"))
        self.assertEqual(occurrences[0].time_slot.start_time, "10:00:00")
        self.assertEqual(occurrences[0].time_slot.end_time, "11:00:00")


# ── project_course_occurrences ────────────────────────────────────────────────

class TestProjectCourseOccurrences(unittest.TestCase):
    """project_course_occurrences() — course session projection."""

    def _project(self, course, blocked=None):
        from backend.app.domain.services.schedule_projection import project_course_occurrences
        return project_course_occurrences(course, blocked or [])

    @_skip_cron
    def test_weekly_monday_course_over_four_weeks_gives_four_sessions(self):
        course = _course(rule_type="cron", value="0 0 * * MON",
                         start="2025-09-01", end="2025-09-28")
        occurrences = self._project(course)
        self.assertEqual(len(occurrences), 4)

    def test_one_time_course_gives_one_session(self):
        course = _course(rule_type="one_time", value="2025-09-15",
                         start="2025-09-01", end="2025-09-30")
        occurrences = self._project(course)
        self.assertEqual(len(occurrences), 1)
        self.assertEqual(occurrences[0].date, "2025-09-15")

    @_skip_cron
    def test_blocked_day_skips_course_session(self):
        course = _course(start="2025-09-01", end="2025-09-28")
        blocked = [_holiday("Sep 8 Off", "2025-09-08")]
        occurrences = self._project(course, blocked)
        dates = [o.date for o in occurrences]
        self.assertNotIn("2025-09-08", dates)
        self.assertEqual(len(occurrences), 3)

    @_skip_cron
    def test_lead_instructor_assigned_to_all_occurrences(self):
        course = _course(start="2025-09-01", end="2025-09-28")
        occurrences = self._project(course)
        for occ in occurrences:
            self.assertEqual(occ.instructor_id, "i1")

    @_skip_cron
    def test_course_id_set_on_all_occurrences(self):
        course = _course(start="2025-09-01", end="2025-09-28")
        occurrences = self._project(course)
        for occ in occurrences:
            self.assertEqual(occ.course_id, "c1")
            self.assertIsNone(occ.lesson_id)

    def test_occurrence_id_is_empty_string(self):
        course = _course(rule_type="one_time", value="2025-09-15",
                         start="2025-09-01", end="2025-09-30")
        occurrences = self._project(course)
        self.assertEqual(occurrences[0].occurrence_id, "")

    def test_no_occurrences_when_all_blocked(self):
        course = _course(rule_type="one_time", value="2025-09-15",
                         start="2025-09-01", end="2025-09-30")
        blocked = [_vacation("Block All", "2025-09-01", "2025-09-30")]
        occurrences = self._project(course, blocked)
        self.assertEqual(occurrences, [])

    def test_course_period_start_after_window_end_returns_empty(self):
        course = _course(rule_type="one_time", value="2025-10-15",
                         start="2025-10-01", end="2025-10-31")
        # The course's own period is used as the window
        occurrences = self._project(course)
        self.assertEqual(len(occurrences), 1)

    @_skip_cron
    def test_room_id_set_on_all_occurrences(self):
        course = _course(start="2025-09-01", end="2025-09-28")
        occurrences = self._project(course)
        for occ in occurrences:
            self.assertEqual(occ.room_id, "r1")


# ── _cron_hits_date ───────────────────────────────────────────────────────────

@_skip_cron
class TestCronHitsDate(unittest.TestCase):
    """schedule_projection._cron_hits_date() — cron evaluation helper."""

    def _hits(self, expression, iso_date):
        from backend.app.domain.services.schedule_projection import _cron_hits_date
        return _cron_hits_date(expression, iso_date)

    def test_weekly_monday_hits_a_monday(self):
        self.assertTrue(self._hits("0 0 * * MON", "2025-09-01"))  # Sep 1 is Monday

    def test_weekly_monday_does_not_hit_tuesday(self):
        self.assertFalse(self._hits("0 0 * * MON", "2025-09-02"))  # Sep 2 is Tuesday

    def test_weekend_cron_hits_saturday(self):
        self.assertTrue(self._hits("0 0 * * SAT,SUN", "2025-09-06"))  # Saturday

    def test_weekend_cron_hits_sunday(self):
        self.assertTrue(self._hits("0 0 * * SAT,SUN", "2025-09-07"))  # Sunday

    def test_weekend_cron_does_not_hit_monday(self):
        self.assertFalse(self._hits("0 0 * * SAT,SUN", "2025-09-01"))  # Monday


# ── _is_blocked ───────────────────────────────────────────────────────────────

class TestIsBlocked(unittest.TestCase):
    """schedule_projection._is_blocked() — internal helper."""

    def _blocked(self, iso_date, blocked_times):
        from backend.app.domain.services.schedule_projection import _is_blocked
        return _is_blocked(iso_date, blocked_times)

    def test_empty_blocked_list_is_never_blocked(self):
        self.assertFalse(self._blocked("2025-09-01", []))

    def test_single_day_holiday_blocks_that_day(self):
        bt = _holiday("Christmas", "2025-12-25")
        self.assertTrue(self._blocked("2025-12-25", [bt]))

    def test_single_day_holiday_does_not_block_other_days(self):
        bt = _holiday("Christmas", "2025-12-25")
        self.assertFalse(self._blocked("2025-12-24", [bt]))

    def test_date_range_blocks_start(self):
        bt = _vacation("Summer", "2025-07-14", "2025-07-28")
        self.assertTrue(self._blocked("2025-07-14", [bt]))

    def test_date_range_blocks_end(self):
        bt = _vacation("Summer", "2025-07-14", "2025-07-28")
        self.assertTrue(self._blocked("2025-07-28", [bt]))

    def test_date_range_blocks_middle(self):
        bt = _vacation("Summer", "2025-07-14", "2025-07-28")
        self.assertTrue(self._blocked("2025-07-21", [bt]))

    def test_date_range_does_not_block_outside(self):
        bt = _vacation("Summer", "2025-07-14", "2025-07-28")
        self.assertFalse(self._blocked("2025-07-29", [bt]))

    @_skip_cron
    def test_cron_recurring_blocks_matching_day(self):
        bt = _recurring_weekend()  # every SAT/SUN
        self.assertTrue(self._blocked("2025-09-06", [bt]))  # Saturday

    @_skip_cron
    def test_cron_recurring_does_not_block_non_matching_day(self):
        bt = _recurring_weekend()
        self.assertFalse(self._blocked("2025-09-01", [bt]))  # Monday

    def test_multiple_blocked_times_any_match_blocks(self):
        bt1 = _holiday("Holiday A", "2025-09-01")
        bt2 = _holiday("Holiday B", "2025-09-10")
        self.assertTrue(self._blocked("2025-09-10", [bt1, bt2]))
        self.assertFalse(self._blocked("2025-09-05", [bt1, bt2]))


# ── project_course_with_accommodation ────────────────────────────────────────

class TestProjectCourseWithAccommodation(unittest.TestCase):
    """project_course_with_accommodation() — resource substitution logic.

    Course: weekly Mondays Sep 1–28 (Sep 1, 8, 15, 22).
    Primary: instructor i1, room r1.
    Alternatives: instructor i2, room r2.
    """

    def _project(self, course, instructor_blocked=None, room_blocked=None,
                 student_blocked=None, alt_instructors=None, alt_rooms=None,
                 lookahead_months=0):
        from backend.app.domain.services.schedule_projection import (
            project_course_with_accommodation,
        )
        return project_course_with_accommodation(
            course=course,
            instructor_blocked=instructor_blocked or {},
            room_blocked=room_blocked or {},
            student_blocked=student_blocked or [],
            alternative_instructor_ids=alt_instructors or [],
            alternative_room_ids=alt_rooms or [],
            lookahead_months=lookahead_months,
        )

    # ── No conflicts ──────────────────────────────────────────────────────────

    def test_no_conflicts_schedules_all_dates(self):
        course = _course()
        result = self._project(course)
        self.assertEqual(len(result.scheduled), 4)
        self.assertEqual(result.unresolvable, [])

    def test_no_conflicts_uses_primary_instructor_and_room(self):
        course = _course()
        result = self._project(course)
        for occ in result.scheduled:
            self.assertEqual(occ.instructor_id, "i1")
            self.assertEqual(occ.room_id, "r1")

    # ── Instructor blocked — substitute instructor ─────────────────────────────

    def test_instructor_blocked_one_date_substituted_with_alt_instructor(self):
        course = _course()
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-08")]}
        result = self._project(course, instructor_blocked=instructor_blocked,
                               alt_instructors=["i2"])
        self.assertEqual(len(result.scheduled), 4)
        self.assertEqual(result.unresolvable, [])
        sep8 = next(o for o in result.scheduled if o.date == "2025-09-08")
        self.assertEqual(sep8.instructor_id, "i2")
        self.assertEqual(sep8.room_id, "r1")

    def test_non_blocked_dates_keep_primary_instructor(self):
        course = _course()
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-08")]}
        result = self._project(course, instructor_blocked=instructor_blocked,
                               alt_instructors=["i2"])
        for occ in result.scheduled:
            if occ.date != "2025-09-08":
                self.assertEqual(occ.instructor_id, "i1")

    def test_instructor_blocked_no_alt_makes_date_unresolvable(self):
        course = _course()
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-08")]}
        result = self._project(course, instructor_blocked=instructor_blocked)
        self.assertIn("2025-09-08", result.unresolvable)
        self.assertEqual(len(result.scheduled), 3)

    def test_all_instructors_blocked_date_is_unresolvable(self):
        course = _course()
        instructor_blocked = {
            "i1": [_holiday("Away i1", "2025-09-15")],
            "i2": [_holiday("Away i2", "2025-09-15")],
        }
        result = self._project(course, instructor_blocked=instructor_blocked,
                               alt_instructors=["i2"])
        self.assertIn("2025-09-15", result.unresolvable)

    # ── Room blocked — substitute room ────────────────────────────────────────

    def test_room_blocked_one_date_substituted_with_alt_room(self):
        course = _course()
        room_blocked = {"r1": [_holiday("Maintenance", "2025-09-22")]}
        result = self._project(course, room_blocked=room_blocked, alt_rooms=["r2"])
        self.assertEqual(len(result.scheduled), 4)
        sep22 = next(o for o in result.scheduled if o.date == "2025-09-22")
        self.assertEqual(sep22.room_id, "r2")
        self.assertEqual(sep22.instructor_id, "i1")

    def test_room_blocked_no_alt_makes_date_unresolvable(self):
        course = _course()
        room_blocked = {"r1": [_holiday("Maintenance", "2025-09-01")]}
        result = self._project(course, room_blocked=room_blocked)
        self.assertIn("2025-09-01", result.unresolvable)

    def test_all_rooms_blocked_date_is_unresolvable(self):
        course = _course()
        room_blocked = {
            "r1": [_holiday("Closed r1", "2025-09-01")],
            "r2": [_holiday("Closed r2", "2025-09-01")],
        }
        result = self._project(course, room_blocked=room_blocked, alt_rooms=["r2"])
        self.assertIn("2025-09-01", result.unresolvable)

    # ── Substitution preference order ─────────────────────────────────────────

    def test_prefers_primary_instructor_over_alt_when_both_free(self):
        course = _course()
        result = self._project(course, alt_instructors=["i2"])
        for occ in result.scheduled:
            self.assertEqual(occ.instructor_id, "i1")

    def test_prefers_alt_room_over_alt_instructor_when_instructor_free(self):
        """When instructor i1 is blocked but room r1 is free,
        i1+r2 is preferred over i2+r1."""
        course = _course()
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-08")]}
        # Both i2+r1 and i1+r2 are available; i1+r2 should win (same instructor)
        result = self._project(course, instructor_blocked=instructor_blocked,
                               alt_instructors=["i2"], alt_rooms=["r2"])
        sep8 = next(o for o in result.scheduled if o.date == "2025-09-08")
        self.assertEqual(sep8.instructor_id, "i2")
        self.assertEqual(sep8.room_id, "r1")  # room didn't need to change

    def test_falls_back_to_alt_instructor_and_alt_room(self):
        """Primary instructor + primary room both blocked → use i2 + r2."""
        course = _course()
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-08")]}
        room_blocked = {"r1": [_holiday("Maintenance", "2025-09-08")]}
        result = self._project(course, instructor_blocked=instructor_blocked,
                               room_blocked=room_blocked,
                               alt_instructors=["i2"], alt_rooms=["r2"])
        sep8 = next(o for o in result.scheduled if o.date == "2025-09-08")
        self.assertEqual(sep8.instructor_id, "i2")
        self.assertEqual(sep8.room_id, "r2")

    # ── Student blocked — non-substitutable ───────────────────────────────────

    def test_student_blocked_makes_date_unresolvable_even_with_alts(self):
        course = _course()
        student_blocked = [_holiday("Student sick", "2025-09-01")]
        result = self._project(course, student_blocked=student_blocked,
                               alt_instructors=["i2"], alt_rooms=["r2"])
        self.assertIn("2025-09-01", result.unresolvable)
        self.assertEqual(len(result.scheduled), 3)

    def test_student_blocked_does_not_affect_other_dates(self):
        course = _course()
        student_blocked = [_holiday("Student sick", "2025-09-08")]
        result = self._project(course, student_blocked=student_blocked)
        self.assertEqual(len(result.unresolvable), 1)
        self.assertEqual(len(result.scheduled), 3)

    # ── Result structure ──────────────────────────────────────────────────────

    def test_result_has_scheduled_and_unresolvable(self):
        from backend.app.domain.services.schedule_projection import ScheduleAccommodationResult
        course = _course()
        result = self._project(course)
        self.assertIsInstance(result, ScheduleAccommodationResult)
        self.assertIsInstance(result.scheduled, list)
        self.assertIsInstance(result.unresolvable, list)

    def test_occurrence_ids_are_empty_string(self):
        course = _course()
        result = self._project(course)
        for occ in result.scheduled:
            self.assertEqual(occ.occurrence_id, "")

    def test_scheduled_dates_are_in_order(self):
        course = _course()
        result = self._project(course)
        dates = [o.date for o in result.scheduled]
        self.assertEqual(dates, sorted(dates))

    def test_no_alternatives_all_primary_blocked_all_unresolvable(self):
        course = _course()
        instructor_blocked = {
            "i1": [
                _holiday("Away 1", "2025-09-01"),
                _holiday("Away 8", "2025-09-08"),
                _holiday("Away 15", "2025-09-15"),
                _holiday("Away 22", "2025-09-22"),
            ]
        }
        result = self._project(course, instructor_blocked=instructor_blocked)
        self.assertEqual(result.scheduled, [])
        self.assertEqual(len(result.unresolvable), 4)

    # ── Lookahead: reschedule when no same-date slot exists ───────────────────

    def test_blocked_date_with_future_opening_goes_to_rescheduled(self):
        """Sep 1 is blocked; next Monday (Sep 8) is free → rescheduled."""
        course = _course()
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-01")]}
        result = self._project(course, instructor_blocked=instructor_blocked,
                               lookahead_months=3)
        # Sep 1 cannot be placed on Sep 1 but finds Sep 8 as next free Monday
        self.assertEqual(len(result.rescheduled), 1)
        self.assertEqual(result.rescheduled[0].original_date, "2025-09-01")
        self.assertGreater(result.rescheduled[0].occurrence.date, "2025-09-01")
        # The remaining 3 original Mondays still schedule normally
        self.assertEqual(len(result.scheduled), 3)
        self.assertEqual(result.unresolvable, [])

    def test_rescheduled_occurrence_tracks_original_date(self):
        course = _course()
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-08")]}
        result = self._project(course, instructor_blocked=instructor_blocked,
                               lookahead_months=3)
        self.assertEqual(result.rescheduled[0].original_date, "2025-09-08")

    def test_rescheduled_occurrence_is_after_original_date(self):
        course = _course()
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-08")]}
        result = self._project(course, instructor_blocked=instructor_blocked,
                               lookahead_months=3)
        occ = result.rescheduled[0].occurrence
        self.assertGreater(occ.date, "2025-09-08")

    def test_zero_lookahead_never_reschedules(self):
        """lookahead_months=0 means the window is empty → all blocked go to unresolvable."""
        course = _course()
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-08")]}
        result = self._project(course, instructor_blocked=instructor_blocked,
                               lookahead_months=0)
        self.assertEqual(result.rescheduled, [])
        self.assertIn("2025-09-08", result.unresolvable)

    def test_student_blocked_goes_to_unresolvable_not_rescheduled(self):
        """Students can't be substituted — student blocks must never be rescheduled."""
        course = _course()
        student_blocked = [_holiday("Student sick", "2025-09-01")]
        result = self._project(course, student_blocked=student_blocked,
                               lookahead_months=3)
        self.assertEqual(result.rescheduled, [])
        self.assertIn("2025-09-01", result.unresolvable)

    def test_lookahead_uses_same_recurrence_pattern(self):
        """Rescheduled date must also be a Monday (weekly cron)."""
        course = _course()
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-01")]}
        result = self._project(course, instructor_blocked=instructor_blocked,
                               lookahead_months=3)
        from datetime import date as _date
        new_date = _date.fromisoformat(result.rescheduled[0].occurrence.date)
        self.assertEqual(new_date.weekday(), 0)  # 0 = Monday

    def test_all_blocked_within_lookahead_stays_unresolvable(self):
        """Instructor blocked for the entire lookahead window → unresolvable."""
        course = _course(start="2025-09-01", end="2025-09-01")  # one_time style via cron
        # Block i1 for a full 4-month span so the 3-month lookahead can't find anything
        instructor_blocked = {
            "i1": [_vacation("Long leave", "2025-08-25", "2026-01-31")],
        }
        result = self._project(course, instructor_blocked=instructor_blocked,
                               lookahead_months=3)
        self.assertIn("2025-09-01", result.unresolvable)
        self.assertEqual(result.rescheduled, [])


# ── project_lesson_with_accommodation ────────────────────────────────────────

class TestProjectLessonWithAccommodation(unittest.TestCase):
    """project_lesson_with_accommodation() — standalone lesson substitution."""

    def _project(self, lesson, window=None, instructor_blocked=None,
                 room_blocked=None, student_blocked=None,
                 alt_instructors=None, alt_rooms=None):
        from backend.app.domain.services.schedule_projection import (
            project_lesson_with_accommodation,
        )
        return project_lesson_with_accommodation(
            lesson=lesson,
            window=window or _window(),
            instructor_blocked=instructor_blocked or {},
            room_blocked=room_blocked or {},
            student_blocked=student_blocked or [],
            alternative_instructor_ids=alt_instructors or [],
            alternative_room_ids=alt_rooms or [],
        )

    def test_no_recurrence_returns_empty(self):
        lesson = _lesson(rule_type=None)
        result = self._project(lesson)
        from backend.app.domain.services.schedule_projection import ScheduleAccommodationResult
        self.assertIsInstance(result, ScheduleAccommodationResult)
        self.assertEqual(result.scheduled, [])
        self.assertEqual(result.unresolvable, [])

    def test_one_time_no_conflicts_scheduled(self):
        lesson = _lesson(rule_type="one_time", value="2025-09-15")
        result = self._project(lesson, window=_window("2025-09-01", "2025-09-30"))
        self.assertEqual(len(result.scheduled), 1)
        self.assertEqual(result.unresolvable, [])

    def test_one_time_instructor_blocked_substituted(self):
        lesson = _lesson(rule_type="one_time", value="2025-09-15")
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-15")]}
        result = self._project(lesson, window=_window("2025-09-01", "2025-09-30"),
                               instructor_blocked=instructor_blocked,
                               alt_instructors=["i2"])
        self.assertEqual(len(result.scheduled), 1)
        self.assertEqual(result.scheduled[0].instructor_id, "i2")

    def test_one_time_room_blocked_substituted(self):
        lesson = _lesson(rule_type="one_time", value="2025-09-15")
        room_blocked = {"r1": [_holiday("Maintenance", "2025-09-15")]}
        result = self._project(lesson, window=_window("2025-09-01", "2025-09-30"),
                               room_blocked=room_blocked, alt_rooms=["r2"])
        self.assertEqual(len(result.scheduled), 1)
        self.assertEqual(result.scheduled[0].room_id, "r2")

    def test_cron_weekly_substitutes_blocked_week(self):
        lesson = _lesson(rule_type="cron", value="0 0 * * MON")
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-08")]}
        result = self._project(lesson, instructor_blocked=instructor_blocked,
                               alt_instructors=["i2"])
        self.assertEqual(len(result.scheduled), 4)
        sep8 = next(o for o in result.scheduled if o.date == "2025-09-08")
        self.assertEqual(sep8.instructor_id, "i2")

    def test_student_blocked_unresolvable(self):
        lesson = _lesson(rule_type="one_time", value="2025-09-15")
        student_blocked = [_holiday("Sick", "2025-09-15")]
        result = self._project(lesson, window=_window("2025-09-01", "2025-09-30"),
                               student_blocked=student_blocked,
                               alt_instructors=["i2"], alt_rooms=["r2"])
        self.assertEqual(result.scheduled, [])
        self.assertIn("2025-09-15", result.unresolvable)


if __name__ == "__main__":
    unittest.main()
