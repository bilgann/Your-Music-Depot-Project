"""
Schedule suggestion application service.

Orchestrates all repository calls needed by the schedule suggestion domain
service and serialises the results for the API layer.
"""
from __future__ import annotations

from backend.app.domain.entities.credential import CredentialEntity
from backend.app.domain.entities.instructor import InstructorEntity
from backend.app.domain.entities.instructor_student_compatibility import (
    InstructorStudentCompatibilityEntity,
)
from backend.app.domain.entities.room import RoomEntity
from backend.app.domain.entities.student import StudentEntity
from backend.app.domain.exceptions.exceptions import NotFoundError, ValidationError
from backend.app.domain.services import compatibility_service
from backend.app.domain.services.schedule_suggestion_service import (
    LessonPlanRequest,
    suggest_schedules,
)
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
from backend.app.domain.value_objects.scheduling.date_range import DateRange
from backend.app.infrastructure.database.repositories import (
    Credential,
    Instructor,
    InstructorStudentCompatibility,
    Room,
    Student,
)


def suggest_lesson_schedule(
    student_id: str,
    plan_data: dict,
    max_suggestions: int = 5,
    min_placement_rate: float = 0.7,
) -> list[dict]:
    """Find up to `max_suggestions` schedule options for a student.

    Args:
        student_id:          Student who will attend the lessons.
        plan_data:           Dict with keys:
                               recurrence          str  (cron or ISO date)
                               period_start        str  (ISO date)
                               period_end          str  (ISO date)
                               start_time          str  ("HH:MM:SS")
                               end_time            str  ("HH:MM:SS")
                               preferred_instructor_ids  list[str]  (optional)
                               preferred_room_ids        list[str]  (optional)
        max_suggestions:     Cap on returned suggestions (default 5).
        min_placement_rate:  Minimum acceptable session placement rate (default 0.7).

    Returns:
        List of suggestion dicts, each with:
          rank, instructor_id, room_id, recurrence, placement_rate,
          total_sessions, scheduled_count, rescheduled_count, unresolvable_count,
          scheduled, rescheduled, unresolvable.

    Raises:
        NotFoundError   if the student does not exist.
        ValidationError if required plan_data fields are missing.
    """
    # ── Validate plan data ─────────────────────────────────────────────────────
    required = ("recurrence", "period_start", "period_end", "start_time", "end_time")
    missing = [f for f in required if not plan_data.get(f)]
    if missing:
        raise ValidationError([
            {"field": f, "message": f"'{f}' is required."} for f in missing
        ])

    # ── Load student ───────────────────────────────────────────────────────────
    srows = Student.get(student_id)
    if not srows:
        raise NotFoundError("Student not found.")
    student = StudentEntity.from_dict(srows[0])

    # ── Build lesson plan ──────────────────────────────────────────────────────
    lesson_plan = LessonPlanRequest(
        recurrence=plan_data["recurrence"],
        period=DateRange(
            period_start=plan_data["period_start"],
            period_end=plan_data["period_end"],
        ),
        start_time=plan_data["start_time"],
        end_time=plan_data["end_time"],
        preferred_instructor_ids=list(plan_data.get("preferred_instructor_ids") or []),
        preferred_room_ids=list(plan_data.get("preferred_room_ids") or []),
    )

    # ── Load instructors + compatibility ───────────────────────────────────────
    all_instructor_rows = Instructor.get_all()
    instructors = [InstructorEntity.from_dict(r) for r in all_instructor_rows]
    all_credentials = [CredentialEntity.from_dict(r) for r in Credential.get_all()]
    all_overrides = [
        InstructorStudentCompatibilityEntity.from_dict(r)
        for r in InstructorStudentCompatibility.get_by_student(student_id)
    ]

    compatible = compatibility_service.filter_compatible(
        student, instructors, all_credentials, all_overrides
    )

    # ── Blocked times ──────────────────────────────────────────────────────────
    instructor_blocked: dict[str, list[BlockedTime]] = {
        instr.instructor_id: instr.blocked_times for instr, _ in compatible
    }

    rooms = [RoomEntity.from_dict(r) for r in Room.get_all()]
    room_blocked: dict[str, list[BlockedTime]] = {
        room.room_id: room.blocked_times for room in rooms
    }

    # Student's own blocked times come from their linked client record.
    # We use a flat merge here; the domain service treats these as non-substitutable.
    student_blocked: list[BlockedTime] = list(student.blocked_times) if hasattr(student, "blocked_times") else []

    # ── Run suggestion engine ──────────────────────────────────────────────────
    suggestions = suggest_schedules(
        lesson_plan=lesson_plan,
        compatible_instructors=compatible,
        instructor_blocked=instructor_blocked,
        rooms=rooms,
        room_blocked=room_blocked,
        student_blocked=student_blocked,
        max_suggestions=max_suggestions,
        min_placement_rate=min_placement_rate,
    )

    # ── Serialise ──────────────────────────────────────────────────────────────
    return [_serialise_suggestion(s) for s in suggestions]


# ── Serialisation helpers ─────────────────────────────────────────────────────

def _serialise_suggestion(s) -> dict:
    return {
        "rank":               s.rank,
        "instructor_id":      s.instructor_id,
        "room_id":            s.room_id,
        "recurrence":         s.recurrence,
        "placement_rate":     s.placement_rate,
        "total_sessions":     s.total_sessions,
        "scheduled_count":    len(s.result.scheduled),
        "rescheduled_count":  len(s.result.rescheduled),
        "unresolvable_count": len(s.result.unresolvable),
        "scheduled": [o.to_dict() for o in s.result.scheduled],
        "rescheduled": [
            {
                "original_date": r.original_date,
                "occurrence": r.occurrence.to_dict(),
            }
            for r in s.result.rescheduled
        ],
        "unresolvable": list(s.result.unresolvable),
    }
