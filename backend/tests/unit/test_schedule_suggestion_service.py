"""
Unit tests for the schedule suggestion domain service.

domain/services/schedule_suggestion_service.py

Tests cover:
  suggest_schedules()   — ranking, placement rate filtering, preference order,
                          max_suggestions cap, edge cases (no instructors, no rooms,
                          all blocked, zero sessions)
  LessonPlanRequest     — property accessors
  _instructor_sort_key  — ordering logic

Calendar reference (2025-09-XX):
  Sep 1  = Monday
  Sep 8  = Monday
  Sep 15 = Monday
  Sep 22 = Monday
  Sep 29 = Monday  (outside 4-week window Sep 1–28)
"""
import unittest

from backend.app.domain.entities.instructor import InstructorEntity
from backend.app.domain.entities.room import RoomEntity
from backend.app.domain.value_objects.compatibility.compatibility_result import (
    CompatibilityResult,
)
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
from backend.app.domain.value_objects.scheduling.date_range import DateRange
from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule


# ── Fixtures ──────────────────────────────────────────────────────────────────

_PERIOD = DateRange("2025-09-01", "2025-09-28")   # 4 Mondays
_WEEKLY_MON = "0 0 * * MON"


def _plan(recurrence=_WEEKLY_MON, start="2025-09-01", end="2025-09-28",
          preferred_instructors=None, preferred_rooms=None):
    from backend.app.domain.services.schedule_suggestion_service import LessonPlanRequest
    return LessonPlanRequest(
        recurrence=recurrence,
        period=DateRange(start, end),
        start_time="10:00:00",
        end_time="11:00:00",
        preferred_instructor_ids=preferred_instructors or [],
        preferred_room_ids=preferred_rooms or [],
    )


def _instructor(instructor_id="i1"):
    return InstructorEntity(instructor_id=instructor_id, person_id="p1")


def _room(room_id="r1"):
    return RoomEntity(room_id=room_id, name=f"Room {room_id}")


def _compat(hard_verdict=None, soft_verdict=None):
    return CompatibilityResult.ok(hard_verdict=hard_verdict, soft_verdict=soft_verdict)


def _holiday(label, date_str):
    return BlockedTime.holiday(label, date_str)


def _suggest(plan, instructors=None, rooms=None, instructor_blocked=None,
             room_blocked=None, student_blocked=None,
             max_suggestions=5, min_placement_rate=0.0, lookahead_months=0):
    from backend.app.domain.services.schedule_suggestion_service import suggest_schedules
    return suggest_schedules(
        lesson_plan=plan,
        compatible_instructors=instructors if instructors is not None else [(_instructor(), _compat())],
        instructor_blocked=instructor_blocked or {},
        rooms=rooms if rooms is not None else [_room()],
        room_blocked=room_blocked or {},
        student_blocked=student_blocked or [],
        max_suggestions=max_suggestions,
        min_placement_rate=min_placement_rate,
        lookahead_months=lookahead_months,
    )


# ── LessonPlanRequest ─────────────────────────────────────────────────────────

class TestLessonPlanRequest(unittest.TestCase):

    def test_recurrence_rule_property_parses_cron(self):
        plan = _plan()
        self.assertEqual(plan.recurrence_rule.rule_type, "cron")
        self.assertEqual(plan.recurrence_rule.value, _WEEKLY_MON)

    def test_recurrence_rule_property_parses_one_time(self):
        plan = _plan(recurrence="2025-09-15")
        self.assertEqual(plan.recurrence_rule.rule_type, "one_time")

    def test_time_slot_property(self):
        plan = _plan()
        self.assertEqual(plan.time_slot.start_time, "10:00:00")
        self.assertEqual(plan.time_slot.end_time, "11:00:00")

    def test_default_preferred_lists_are_empty(self):
        plan = _plan()
        self.assertEqual(plan.preferred_instructor_ids, [])
        self.assertEqual(plan.preferred_room_ids, [])


# ── suggest_schedules — basic behaviour ───────────────────────────────────────

class TestSuggestSchedulesBasic(unittest.TestCase):

    def test_returns_list(self):
        result = _suggest(_plan())
        self.assertIsInstance(result, list)

    def test_no_instructors_returns_empty(self):
        result = _suggest(_plan(), instructors=[])
        self.assertEqual(result, [])

    def test_no_rooms_returns_empty(self):
        result = _suggest(_plan(), rooms=[])
        self.assertEqual(result, [])

    def test_zero_session_period_returns_empty(self):
        # Period where no Monday falls (e.g. Mon–Fri of a week starting Tuesday)
        plan = _plan(start="2025-09-02", end="2025-09-06")  # Tue–Sat, no Monday
        result = _suggest(plan)
        self.assertEqual(result, [])

    def test_single_instructor_single_room_returns_one_suggestion(self):
        result = _suggest(_plan())
        self.assertEqual(len(result), 1)

    def test_suggestion_has_expected_keys(self):
        from backend.app.domain.services.schedule_suggestion_service import ScheduleSuggestion
        result = _suggest(_plan())
        self.assertIsInstance(result[0], ScheduleSuggestion)
        self.assertIsNotNone(result[0].instructor_id)
        self.assertIsNotNone(result[0].room_id)
        self.assertIsNotNone(result[0].recurrence)
        self.assertIsNotNone(result[0].placement_rate)
        self.assertIsNotNone(result[0].total_sessions)
        self.assertIsNotNone(result[0].result)

    def test_total_sessions_matches_recurrence(self):
        result = _suggest(_plan())
        self.assertEqual(result[0].total_sessions, 4)  # 4 Mondays in Sep 1–28

    def test_rank_starts_at_one(self):
        result = _suggest(_plan())
        self.assertEqual(result[0].rank, 1)

    def test_no_conflicts_placement_rate_is_one(self):
        result = _suggest(_plan())
        self.assertAlmostEqual(result[0].placement_rate, 1.0)

    def test_recurrence_on_suggestion_matches_plan(self):
        plan = _plan()
        result = _suggest(plan)
        self.assertEqual(result[0].recurrence, _WEEKLY_MON)


# ── suggest_schedules — placement rate filtering ──────────────────────────────

class TestSuggestSchedulesPlacementFilter(unittest.TestCase):

    def test_fully_blocked_instructor_below_threshold_excluded(self):
        """Instructor blocked on all 4 dates → placement 0 → excluded at default threshold."""
        instructor_blocked = {
            "i1": [
                _holiday("A", "2025-09-01"), _holiday("B", "2025-09-08"),
                _holiday("C", "2025-09-15"), _holiday("D", "2025-09-22"),
            ]
        }
        result = _suggest(_plan(), instructor_blocked=instructor_blocked,
                          min_placement_rate=0.7)
        self.assertEqual(result, [])

    def test_three_of_four_dates_placed_passes_0_7_threshold(self):
        """3/4 sessions = 0.75 placement rate → accepted at 0.7 threshold."""
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-01")]}
        result = _suggest(_plan(), instructor_blocked=instructor_blocked,
                          min_placement_rate=0.7)
        self.assertEqual(len(result), 1)
        self.assertGreaterEqual(result[0].placement_rate, 0.7)

    def test_min_placement_rate_zero_accepts_everything(self):
        instructor_blocked = {
            "i1": [
                _holiday("A", "2025-09-01"), _holiday("B", "2025-09-08"),
                _holiday("C", "2025-09-15"), _holiday("D", "2025-09-22"),
            ]
        }
        result = _suggest(_plan(), instructor_blocked=instructor_blocked,
                          min_placement_rate=0.0)
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0].placement_rate, 0.0)

    def test_placement_rate_counts_rescheduled_sessions(self):
        """Sessions placed via lookahead should count toward placement rate."""
        instructor_blocked = {"i1": [_holiday("Away", "2025-09-01")]}
        # With lookahead=3 the blocked Sep 1 should be rescheduled to a future Monday
        result = _suggest(_plan(), instructor_blocked=instructor_blocked,
                          min_placement_rate=1.0, lookahead_months=3)
        # All 4 sessions placed (3 scheduled + 1 rescheduled) → rate = 1.0
        self.assertAlmostEqual(result[0].placement_rate, 1.0)


# ── suggest_schedules — max_suggestions cap ───────────────────────────────────

class TestSuggestSchedulesMaxCap(unittest.TestCase):

    def test_max_suggestions_caps_result(self):
        instructors = [(_instructor(f"i{n}"), _compat()) for n in range(1, 10)]
        rooms = [_room(f"r{n}") for n in range(1, 10)]
        result = _suggest(_plan(), instructors=instructors, rooms=rooms,
                          max_suggestions=3)
        self.assertLessEqual(len(result), 3)

    def test_max_suggestions_one_returns_only_best(self):
        instructors = [(_instructor(f"i{n}"), _compat()) for n in range(1, 4)]
        result = _suggest(_plan(), instructors=instructors, max_suggestions=1)
        self.assertEqual(len(result), 1)

    def test_ranks_are_sequential_from_one(self):
        instructors = [(_instructor(f"i{n}"), _compat()) for n in range(1, 4)]
        result = _suggest(_plan(), instructors=instructors, max_suggestions=5)
        for expected, s in enumerate(result, start=1):
            self.assertEqual(s.rank, expected)


# ── suggest_schedules — preference ordering ───────────────────────────────────

class TestSuggestSchedulesOrdering(unittest.TestCase):

    def test_preferred_instructor_comes_first(self):
        instructors = [
            (_instructor("i1"), _compat()),
            (_instructor("i2"), _compat()),
        ]
        plan = _plan(preferred_instructors=["i2"])
        result = _suggest(plan, instructors=instructors, max_suggestions=5)
        self.assertEqual(result[0].instructor_id, "i2")

    def test_preferred_room_comes_first(self):
        rooms = [_room("r1"), _room("r2")]
        plan = _plan(preferred_rooms=["r2"])
        result = _suggest(plan, rooms=rooms, max_suggestions=5)
        self.assertEqual(result[0].room_id, "r2")

    def test_required_instructor_comes_before_neutral(self):
        instructors = [
            (_instructor("i1"), _compat()),                           # neutral
            (_instructor("i2"), _compat(hard_verdict="required")),    # required
        ]
        result = _suggest(_plan(), instructors=instructors, max_suggestions=5)
        self.assertEqual(result[0].instructor_id, "i2")

    def test_preferred_compat_comes_before_neutral(self):
        instructors = [
            (_instructor("i1"), _compat()),                           # neutral
            (_instructor("i2"), _compat(soft_verdict="preferred")),   # preferred
        ]
        result = _suggest(_plan(), instructors=instructors, max_suggestions=5)
        self.assertEqual(result[0].instructor_id, "i2")

    def test_disliked_compat_comes_after_neutral(self):
        instructors = [
            (_instructor("i1"), _compat(soft_verdict="disliked")),    # disliked
            (_instructor("i2"), _compat()),                           # neutral
        ]
        result = _suggest(_plan(), instructors=instructors, max_suggestions=5)
        self.assertEqual(result[0].instructor_id, "i2")

    def test_preferred_instructor_overrides_required_compat(self):
        """Explicit user preference beats automatic compatibility verdict ordering."""
        instructors = [
            (_instructor("i1"), _compat(hard_verdict="required")),
            (_instructor("i2"), _compat()),
        ]
        plan = _plan(preferred_instructors=["i2"])
        result = _suggest(plan, instructors=instructors, max_suggestions=5)
        self.assertEqual(result[0].instructor_id, "i2")

    def test_multiple_rooms_per_instructor_all_appear(self):
        rooms = [_room("r1"), _room("r2"), _room("r3")]
        result = _suggest(_plan(), rooms=rooms, max_suggestions=5)
        room_ids = {s.room_id for s in result}
        self.assertEqual(room_ids, {"r1", "r2", "r3"})


# ── suggest_schedules — result structure ──────────────────────────────────────

class TestSuggestSchedulesResultStructure(unittest.TestCase):

    def test_result_field_is_accommodation_result(self):
        from backend.app.domain.services.schedule_projection import ScheduleAccommodationResult
        result = _suggest(_plan())
        self.assertIsInstance(result[0].result, ScheduleAccommodationResult)

    def test_scheduled_count_equals_total_when_no_blocks(self):
        result = _suggest(_plan())
        self.assertEqual(len(result[0].result.scheduled), 4)
        self.assertEqual(result[0].result.unresolvable, [])

    def test_one_time_recurrence_gives_one_session(self):
        plan = _plan(recurrence="2025-09-15", start="2025-09-01", end="2025-09-30")
        result = _suggest(plan)
        self.assertEqual(result[0].total_sessions, 1)
        self.assertEqual(len(result[0].result.scheduled), 1)


if __name__ == "__main__":
    unittest.main()
