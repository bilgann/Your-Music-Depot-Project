"""
Schedule suggestion domain service.

Given a student's desired lesson plan and a pre-loaded pool of compatible
instructors and available rooms, this service generates up to N ranked schedule
suggestions by iterating through instructor/room combinations and projecting
each one with the accommodation logic.

No database access.  The application service is responsible for loading:
  - Compatible (instructor, CompatibilityResult) pairs via compatibility_service
  - Blocked times per instructor and per room
  - Merged student/client blocked times
  - The full room list

Algorithm
---------
  1. Order instructors by preference signal: user-requested first, then by
     compatibility verdict (required → preferred → neutral → disliked).
  2. Order rooms by preference signal: user-requested first, then others.
  3. For each (instructor, room) pair project with accommodation.
  4. Score: placement_rate = (scheduled + rescheduled) / total_sessions
  5. Accept suggestions where placement_rate >= min_placement_rate (default 0.7).
  6. Stop once max_suggestions (default 5) decent suggestions are collected.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from backend.app.domain.entities.instructor import InstructorEntity
from backend.app.domain.entities.lesson import LessonEntity
from backend.app.domain.entities.room import RoomEntity
from backend.app.domain.services.schedule_projection import (
    RescheduledOccurrence,
    ScheduleAccommodationResult,
    count_occurrences,
    project_lesson_with_accommodation,
)
from backend.app.domain.value_objects.compatibility.compatibility_result import (
    CompatibilityResult,
)
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
from backend.app.domain.value_objects.scheduling.date_range import DateRange
from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
from backend.app.domain.value_objects.scheduling.time_slot import TimeSlot

_LOOKAHEAD_MONTHS: int = int(os.getenv("SCHEDULE_LOOKAHEAD_MONTHS", "3"))

# Ordering weights for compatibility verdicts
_HARD_ORDER = {"required": 0}
_SOFT_ORDER = {"preferred": 0, "disliked": 2}


# ── Value objects ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LessonPlanRequest:
    """What the student/admin submits when requesting a lesson schedule.

    recurrence              Cron expression for the desired schedule, e.g.
                            "0 10 * * MON" (Mondays at 10:00).  One-time ISO
                            dates are also accepted ("2025-09-15").
    period                  The date range over which lessons should run.
    start_time / end_time   Wall-clock bounds for each session.
    preferred_instructor_ids
                            Ordered list of instructor IDs the student or admin
                            would prefer.  Listed candidates are tried before
                            the rest of the compatible pool.
    preferred_room_ids      Same priority hint for rooms.
    """
    recurrence: str
    period: DateRange
    start_time: str
    end_time: str
    preferred_instructor_ids: list[str] = field(default_factory=list)
    preferred_room_ids: list[str] = field(default_factory=list)

    @property
    def recurrence_rule(self) -> RecurrenceRule:
        return RecurrenceRule.from_str(self.recurrence)

    @property
    def time_slot(self) -> TimeSlot:
        return TimeSlot(self.start_time, self.end_time)


@dataclass(frozen=True)
class ScheduleSuggestion:
    """A single ranked schedule suggestion returned to the caller.

    rank            1-based position in the suggestion list (1 = best).
    instructor_id   Proposed instructor for this suggestion.
    room_id         Proposed room for this suggestion.
    recurrence      The recurrence expression used (same as the request for now).
    placement_rate  Fraction of sessions that could be placed, including
                    rescheduled ones.  Range 0.0–1.0.
    total_sessions  Total sessions the recurrence produces over the period.
    result          Full ScheduleAccommodationResult for this combination.
    """
    rank: int
    instructor_id: str
    room_id: str
    recurrence: str
    placement_rate: float
    total_sessions: int
    result: ScheduleAccommodationResult


# ── Domain service ─────────────────────────────────────────────────────────────

def suggest_schedules(
    lesson_plan: LessonPlanRequest,
    compatible_instructors: list[tuple[InstructorEntity, CompatibilityResult]],
    instructor_blocked: dict[str, list[BlockedTime]],
    rooms: list[RoomEntity],
    room_blocked: dict[str, list[BlockedTime]],
    student_blocked: list[BlockedTime],
    max_suggestions: int = 5,
    min_placement_rate: float = 0.7,
    lookahead_months: int = _LOOKAHEAD_MONTHS,
) -> list[ScheduleSuggestion]:
    """Generate up to `max_suggestions` ranked schedule suggestions.

    Args:
        lesson_plan:             The student's desired lesson parameters.
        compatible_instructors:  Pre-filtered (instructor, CompatibilityResult)
                                 pairs from compatibility_service.filter_compatible().
                                 Already sorted by verdict; this service re-orders
                                 only to honour preference hints from the plan.
        instructor_blocked:      {instructor_id: [BlockedTime]} for all candidates.
        rooms:                   All rooms the application layer considers eligible
                                 (e.g. have the right instruments, enough capacity).
        room_blocked:            {room_id: [BlockedTime]} for all candidate rooms.
        student_blocked:         Merged blocked times for enrolled students.
        max_suggestions:         Maximum suggestions to return (1–5 typical).
        min_placement_rate:      Minimum fraction of sessions that must be placeable
                                 (scheduled + rescheduled / total) for a suggestion
                                 to be accepted.  Default 0.7 (70 %).
        lookahead_months:        Months to search ahead when a session date is fully
                                 blocked.  Sourced from SCHEDULE_LOOKAHEAD_MONTHS env
                                 var by default.

    Returns:
        List of ScheduleSuggestion ordered best-first (preferred resources, highest
        placement rate).  May be shorter than max_suggestions if fewer combinations
        meet min_placement_rate.
    """
    if not compatible_instructors or not rooms:
        return []

    total_sessions = count_occurrences(lesson_plan.recurrence_rule, lesson_plan.period)
    if total_sessions == 0:
        return []

    preferred_instructor_ids = set(lesson_plan.preferred_instructor_ids)
    preferred_room_ids = set(lesson_plan.preferred_room_ids)

    sorted_instructors = sorted(
        compatible_instructors,
        key=lambda p: _instructor_sort_key(p, preferred_instructor_ids),
    )
    sorted_rooms = sorted(
        rooms,
        key=lambda r: (0 if r.room_id in preferred_room_ids else 1),
    )

    suggestions: list[ScheduleSuggestion] = []

    for instructor, _compat in sorted_instructors:
        for room in sorted_rooms:
            lesson = _make_synthetic_lesson(
                instructor.instructor_id,
                room.room_id,
                lesson_plan,
            )
            result = project_lesson_with_accommodation(
                lesson=lesson,
                window=lesson_plan.period,
                instructor_blocked=instructor_blocked,
                room_blocked=room_blocked,
                student_blocked=student_blocked,
                lookahead_months=lookahead_months,
            )

            placed = len(result.scheduled) + len(result.rescheduled)
            rate = placed / total_sessions

            if rate >= min_placement_rate:
                suggestions.append(ScheduleSuggestion(
                    rank=len(suggestions) + 1,
                    instructor_id=instructor.instructor_id,
                    room_id=room.room_id,
                    recurrence=lesson_plan.recurrence,
                    placement_rate=round(rate, 4),
                    total_sessions=total_sessions,
                    result=result,
                ))
                if len(suggestions) >= max_suggestions:
                    return suggestions

    return suggestions


# ── Private helpers ────────────────────────────────────────────────────────────

def _instructor_sort_key(
    pair: tuple[InstructorEntity, CompatibilityResult],
    preferred_ids: set[str],
) -> tuple[int, int, int]:
    """Lower value = higher priority."""
    instructor, result = pair
    is_preferred = 0 if instructor.instructor_id in preferred_ids else 1
    hard = _HARD_ORDER.get(result.hard_verdict or "", 1)
    soft = _SOFT_ORDER.get(result.soft_verdict or "", 1)
    return (is_preferred, hard, soft)


def _make_synthetic_lesson(
    instructor_id: str,
    room_id: str,
    plan: LessonPlanRequest,
) -> LessonEntity:
    """Build a temporary LessonEntity template for projection."""
    return LessonEntity(
        lesson_id="__suggestion__",
        instructor_id=instructor_id,
        room_id=room_id,
        time_slot=plan.time_slot,
        recurrence=plan.recurrence_rule,
    )
