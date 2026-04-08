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

import calendar
import os
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta

from croniter import croniter

from backend.app.domain.entities.course import CourseEntity
from backend.app.domain.entities.lesson import LessonEntity
from backend.app.domain.entities.lesson_occurrence import LessonOccurrenceEntity
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
from backend.app.domain.value_objects.scheduling.date_range import DateRange
from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule

# Maximum months to search forward when a date cannot be accommodated.
# Override with the SCHEDULE_LOOKAHEAD_MONTHS environment variable.
_LOOKAHEAD_MONTHS: int = int(os.getenv("SCHEDULE_LOOKAHEAD_MONTHS", "3"))


@dataclass(frozen=True)
class RescheduledOccurrence:
    """An occurrence that could not be placed on its original date and was
    moved to the next available opening found within the lookahead window."""
    original_date: str                # the originally planned ISO date
    occurrence: LessonOccurrenceEntity  # occurrence with the rescheduled date


@dataclass(frozen=True)
class ScheduleAccommodationResult:
    """Result of a project-with-accommodation run.

    scheduled     — occurrences placed on their original date.  Each occurrence
                    carries the instructor_id and room_id that was actually used
                    (may differ from the course template when a substitution was made).
    rescheduled   — occurrences that couldn't be placed on their original date
                    but found a free opening within the lookahead window.
    unresolvable  — ISO dates where even the lookahead found no available slot.
    """
    scheduled: list[LessonOccurrenceEntity]
    rescheduled: list[RescheduledOccurrence] = field(default_factory=list)
    unresolvable: list[str] = field(default_factory=list)


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


def count_occurrences(recurrence: RecurrenceRule, window: DateRange) -> int:
    """Return the total number of dates the recurrence fires within `window`."""
    return len(_expand_recurrence(recurrence.rule_type, recurrence.value, window))


def project_course_with_accommodation(
    course: CourseEntity,
    instructor_blocked: dict[str, list[BlockedTime]],
    room_blocked: dict[str, list[BlockedTime]],
    student_blocked: list[BlockedTime],
    alternative_instructor_ids: list[str] | None = None,
    alternative_room_ids: list[str] | None = None,
    lookahead_months: int = _LOOKAHEAD_MONTHS,
) -> ScheduleAccommodationResult:
    """Project a course, substituting instructors or rooms for blocked dates.

    For each candidate date the function walks an ordered list of
    (instructor, room) pairs and picks the first combination that is free.
    Student blocked times are not substitutable — any date they cover is
    immediately unresolvable.

    When every combination is blocked for a given date, the function searches
    forward through the recurrence pattern (up to `lookahead_months` months)
    for the next free slot.  Dates found this way are returned in `rescheduled`.
    Dates with no opening even within the lookahead window go to `unresolvable`.

    Substitution preference per date:
      1. lead instructor   + primary room      (no substitution)
      2. lead instructor   + alternative room
      3. alternative instructor + primary room
      4. alternative instructor + alternative room

    Args:
        course:                     CourseEntity template.
        instructor_blocked:         {instructor_id: [BlockedTime]} for every
                                    candidate instructor (lead + alternatives).
        room_blocked:               {room_id: [BlockedTime]} for every
                                    candidate room (primary + alternatives).
        student_blocked:            merged blocked times for enrolled students —
                                    these cannot be substituted around.
        alternative_instructor_ids: fallback instructors to try, in priority order.
        alternative_room_ids:       fallback rooms to try, in priority order.
        lookahead_months:           months to search ahead when no same-date slot
                                    is available.  Defaults to
                                    SCHEDULE_LOOKAHEAD_MONTHS env var (3).

    Returns:
        ScheduleAccommodationResult.
    """
    alt_instructors = list(alternative_instructor_ids or [])
    alt_rooms = list(alternative_room_ids or [])

    primary_instructor = course.lead_instructor_id
    primary_room = course.room_id

    # Build ordered (instructor_id, room_id) candidates — least disruptive first
    candidates: list[tuple[str, str]] = [
        (primary_instructor, primary_room),
        *((primary_instructor, r) for r in alt_rooms),
        *((i, primary_room) for i in alt_instructors),
        *((i, r) for i in alt_instructors for r in alt_rooms),
    ]

    candidate_dates = _expand_recurrence(
        course.recurrence.rule_type,
        course.recurrence.value,
        course.period,
    )

    scheduled: list[LessonOccurrenceEntity] = []
    rescheduled: list[RescheduledOccurrence] = []
    unresolvable: list[str] = []

    for iso_date in candidate_dates:
        if _is_blocked(iso_date, student_blocked):
            unresolvable.append(iso_date)
            continue

        placed = False
        for instructor_id, room_id in candidates:
            instr_bt = instructor_blocked.get(instructor_id, [])
            room_bt = room_blocked.get(room_id, [])
            if not _is_blocked(iso_date, instr_bt) and not _is_blocked(iso_date, room_bt):
                occ = _make_course_occurrence(course, iso_date)
                if instructor_id != primary_instructor or room_id != primary_room:
                    occ = replace(occ, instructor_id=instructor_id, room_id=room_id)
                scheduled.append(occ)
                placed = True
                break

        if not placed:
            opening = _find_next_opening(
                course.recurrence.rule_type,
                course.recurrence.value,
                iso_date,
                candidates,
                instructor_blocked,
                room_blocked,
                student_blocked,
                lookahead_months,
            )
            if opening:
                new_date, instructor_id, room_id = opening
                occ = _make_course_occurrence(course, new_date)
                if instructor_id != primary_instructor or room_id != primary_room:
                    occ = replace(occ, instructor_id=instructor_id, room_id=room_id)
                rescheduled.append(RescheduledOccurrence(original_date=iso_date, occurrence=occ))
            else:
                unresolvable.append(iso_date)

    return ScheduleAccommodationResult(
        scheduled=scheduled,
        rescheduled=rescheduled,
        unresolvable=unresolvable,
    )


def project_lesson_with_accommodation(
    lesson: LessonEntity,
    window: DateRange,
    instructor_blocked: dict[str, list[BlockedTime]],
    room_blocked: dict[str, list[BlockedTime]],
    student_blocked: list[BlockedTime],
    alternative_instructor_ids: list[str] | None = None,
    alternative_room_ids: list[str] | None = None,
    lookahead_months: int = _LOOKAHEAD_MONTHS,
) -> ScheduleAccommodationResult:
    """Project a standalone lesson, substituting instructor or room for blocked dates.

    Identical accommodation logic to project_course_with_accommodation but for
    standalone LessonEntity templates.  When all combinations for a date are
    blocked, searches forward through the recurrence up to `lookahead_months`
    months for the next free slot.

    Args:
        lesson:                     LessonEntity template (must have a recurrence rule).
        window:                     date range to project into.
        instructor_blocked:         {instructor_id: [BlockedTime]} for all candidates.
        room_blocked:               {room_id: [BlockedTime]} for all candidates.
        student_blocked:            merged blocked times for enrolled students.
        alternative_instructor_ids: fallback instructors, in priority order.
        alternative_room_ids:       fallback rooms, in priority order.
        lookahead_months:           months to search ahead on failure.  Defaults to
                                    SCHEDULE_LOOKAHEAD_MONTHS env var (3).

    Returns:
        ScheduleAccommodationResult.
    """
    if lesson.recurrence is None:
        return ScheduleAccommodationResult(scheduled=[])

    alt_instructors = list(alternative_instructor_ids or [])
    alt_rooms = list(alternative_room_ids or [])

    primary_instructor = lesson.instructor_id
    primary_room = lesson.room_id

    candidates: list[tuple[str, str]] = [
        (primary_instructor, primary_room),
        *((primary_instructor, r) for r in alt_rooms),
        *((i, primary_room) for i in alt_instructors),
        *((i, r) for i in alt_instructors for r in alt_rooms),
    ]

    candidate_dates = _expand_recurrence(
        lesson.recurrence.rule_type,
        lesson.recurrence.value,
        window,
    )

    scheduled: list[LessonOccurrenceEntity] = []
    rescheduled: list[RescheduledOccurrence] = []
    unresolvable: list[str] = []

    for iso_date in candidate_dates:
        if _is_blocked(iso_date, student_blocked):
            unresolvable.append(iso_date)
            continue

        placed = False
        for instructor_id, room_id in candidates:
            instr_bt = instructor_blocked.get(instructor_id, [])
            room_bt = room_blocked.get(room_id, [])
            if not _is_blocked(iso_date, instr_bt) and not _is_blocked(iso_date, room_bt):
                occ = _make_lesson_occurrence(lesson, iso_date)
                if instructor_id != primary_instructor or room_id != primary_room:
                    occ = replace(occ, instructor_id=instructor_id, room_id=room_id)
                scheduled.append(occ)
                placed = True
                break

        if not placed:
            opening = _find_next_opening(
                lesson.recurrence.rule_type,
                lesson.recurrence.value,
                iso_date,
                candidates,
                instructor_blocked,
                room_blocked,
                student_blocked,
                lookahead_months,
            )
            if opening:
                new_date, instructor_id, room_id = opening
                occ = _make_lesson_occurrence(lesson, new_date)
                if instructor_id != primary_instructor or room_id != primary_room:
                    occ = replace(occ, instructor_id=instructor_id, room_id=room_id)
                rescheduled.append(RescheduledOccurrence(original_date=iso_date, occurrence=occ))
            else:
                unresolvable.append(iso_date)

    return ScheduleAccommodationResult(
        scheduled=scheduled,
        rescheduled=rescheduled,
        unresolvable=unresolvable,
    )


# ── Private helpers ───────────────────────────────────────────────────────────

def _expand_recurrence(rule_type: str, value: str, window: DateRange) -> list[str]:
    """Return all ISO date strings produced by the recurrence within the window."""
    start = date.fromisoformat(window.period_start)
    end   = date.fromisoformat(window.period_end)

    if rule_type == "one_time":
        d = date.fromisoformat(value)
        return [value] if start <= d <= end else []

    # cron — iterate from one day before start so the first occurrence isn't missed
    anchor = datetime(*(start - timedelta(days=1)).timetuple()[:3])
    cron   = croniter(value, anchor)
    dates: list[str] = []
    while True:
        next_date = cron.get_next(datetime).date()
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
    anchor = datetime(*(target - timedelta(days=1)).timetuple()[:3])
    cron   = croniter(expression, anchor)
    next_hit = cron.get_next(datetime).date()
    return next_hit == target


def _add_months(d: date, months: int) -> date:
    """Return `d` shifted forward by `months` calendar months."""
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _find_next_opening(
    rule_type: str,
    recurrence_value: str,
    after_date: str,
    candidates: list[tuple[str, str]],
    instructor_blocked: dict[str, list[BlockedTime]],
    room_blocked: dict[str, list[BlockedTime]],
    student_blocked: list[BlockedTime],
    lookahead_months: int,
) -> tuple[str, str, str] | None:
    """Search the recurrence pattern beyond `after_date` for the next free slot.

    Returns (iso_date, instructor_id, room_id) of the first opening found, or
    None if no slot is available within `lookahead_months` months or the rule
    has no future occurrences (one_time).
    """
    if rule_type == "one_time":
        return None  # single-date events have no future occurrences to look ahead to

    search_start = date.fromisoformat(after_date) + timedelta(days=1)
    search_end = _add_months(search_start, lookahead_months)
    lookahead_window = DateRange(
        period_start=search_start.isoformat(),
        period_end=search_end.isoformat(),
    )
    future_dates = _expand_recurrence(rule_type, recurrence_value, lookahead_window)

    for iso_date in future_dates:
        if _is_blocked(iso_date, student_blocked):
            continue
        for instructor_id, room_id in candidates:
            instr_bt = instructor_blocked.get(instructor_id, [])
            room_bt = room_blocked.get(room_id, [])
            if not _is_blocked(iso_date, instr_bt) and not _is_blocked(iso_date, room_bt):
                return iso_date, instructor_id, room_id

    return None


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
