"""
Schedule projection domain service.

Expands a LessonEntity or CourseEntity template into concrete
LessonOccurrenceEntity records for a given date window, filtering out any
dates blocked by participants.

No database access.  The caller (application service) is responsible for:
  - Loading all relevant blocked_times from instructor, room, and students/clients
  - Persisting the returned occurrences
  - Re-projecting when any blocked_time is added or removed

Requires: croniter  (pip install croniter)
"""

from __future__ import annotations

from datetime import date, timedelta

from croniter import croniter

from backend.app.domain.entities.course import CourseEntity
from backend.app.domain.entities.lesson import LessonEntity
from backend.app.domain.entities.lesson_occurrence import LessonOccurrenceEntity
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
from backend.app.domain.value_objects.scheduling.date_range import DateRange


def project_occurrences(
    lesson: LessonEntity,
    window: DateRange,
    blocked_times: list[BlockedTime],
) -> list[LessonOccurrenceEntity]:
    """
    Expand a standalone lesson template into occurrence stubs for every
    unblocked date within `window`.

    Args:
        lesson:        the LessonEntity template (must have a recurrence rule)
        window:        the date range to project into
        blocked_times: combined blocked times from all participants
                       (instructor + room + each student's client)

    Returns:
        list of LessonOccurrenceEntity — occurrence_id is empty string;
        the caller must assign IDs on persistence.
    """
    if lesson.recurrence is None:
        return []

    candidate_dates = _expand_recurrence(lesson.recurrence.rule_type,
                                          lesson.recurrence.value,
                                          window)
    return [
        _make_lesson_occurrence(lesson, d)
        for d in candidate_dates
        if not _is_blocked(d, blocked_times)
    ]


def project_course_occurrences(
    course: CourseEntity,
    blocked_times: list[BlockedTime],
) -> list[LessonOccurrenceEntity]:
    """
    Expand a course into occurrence stubs for every unblocked session date
    within the course's own period.

    The lead instructor (instructor_ids[0]) is assigned to every occurrence;
    the application layer may reassign co-instructors per occurrence after
    projection.

    Args:
        course:        the CourseEntity template
        blocked_times: combined blocked times from all participants
                       (all instructors + room + all enrolled students' clients)

    Returns:
        list of LessonOccurrenceEntity — occurrence_id is empty string;
        the caller must assign IDs on persistence.
    """
    candidate_dates = _expand_recurrence(
        course.recurrence.rule_type,
        course.recurrence.value,
        course.period,
    )
    return [
        _make_course_occurrence(course, d)
        for d in candidate_dates
        if not _is_blocked(d, blocked_times)
    ]


# ── Private helpers ───────────────────────────────────────────────────────────

def _expand_recurrence(rule_type: str, value: str, window: DateRange) -> list[str]:
    """Return all ISO date strings produced by the recurrence within the window."""
    start = date.fromisoformat(window.period_start)
    end   = date.fromisoformat(window.period_end)

    if rule_type == "one_time":
        d = date.fromisoformat(value)
        return [value] if start <= d <= end else []

    # cron — iterate from one day before start so the first occurrence isn't missed
    anchor = start - timedelta(days=1)
    cron   = croniter(value, anchor)
    dates: list[str] = []
    while True:
        next_date = cron.get_next(date)
        if next_date > end:
            break
        if next_date >= start:
            dates.append(next_date.isoformat())
    return dates


def _is_blocked(iso_date: str, blocked_times: list[BlockedTime]) -> bool:
    """Return True if any BlockedTime covers the given date."""
    for bt in blocked_times:
        # Single-day and date-range checks
        if bt.includes_date(iso_date):
            return True
        # Recurring blocked times (cron) — e.g. every weekend
        if bt.recurrence and bt.recurrence.rule_type == "cron":
            if _cron_hits_date(bt.recurrence.value, iso_date):
                return True
    return False


def _cron_hits_date(expression: str, iso_date: str) -> bool:
    """Return True if the cron expression fires on the given ISO date."""
    target = date.fromisoformat(iso_date)
    anchor = target - timedelta(days=1)
    cron   = croniter(expression, anchor)
    next_hit = cron.get_next(date)
    return next_hit == target


def _make_lesson_occurrence(lesson: LessonEntity, iso_date: str) -> LessonOccurrenceEntity:
    """Build an occurrence stub from a standalone lesson template."""
    return LessonOccurrenceEntity(
        occurrence_id="",           # assigned by persistence layer
        date=iso_date,
        time_slot=lesson.time_slot,
        instructor_id=lesson.instructor_id,
        room_id=lesson.room_id,
        lesson_id=lesson.lesson_id,
        course_id=lesson.course_id,
        rate=lesson.rate,
    )


def _make_course_occurrence(course: CourseEntity, iso_date: str) -> LessonOccurrenceEntity:
    """Build an occurrence stub from a course template for a specific date."""
    return LessonOccurrenceEntity(
        occurrence_id="",           # assigned by persistence layer
        date=iso_date,
        time_slot=course.time_slot,
        instructor_id=course.lead_instructor_id,
        room_id=course.room_id,
        lesson_id=None,
        course_id=course.course_id,
        rate=course.rate,
    )
