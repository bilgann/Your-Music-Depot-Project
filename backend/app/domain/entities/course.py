"""
CourseEntity

A course is the top-level aggregate for a music program — it groups a roster
of students and instructors around a recurring schedule in a specific room.
Individual sessions are materialised as LessonOccurrenceEntity records by the
ScheduleProjectionService.

Use-cases
---------
- Group class: "Beginner Guitar — Spring 2025", 6 students, weekly Tuesdays 4–5 pm
- Private lesson series: 1 student, 1 instructor, every Wednesday 3–4 pm
- Workshop: 1 session (one_time recurrence), multiple instructors

Fields
------
course_id           Surrogate key.
name                Human-readable course name.
description         Optional longer description or syllabus notes.
room_id             The room where sessions are held.
instructor_ids      Ordered list — index 0 is the lead instructor.  Additional
                    entries are co-instructors or assistants.
student_ids         Enrolled student roster.  Maintained by the application layer;
                    individual attendance is tracked on LessonEnrollmentEntity.
period              DateRange covering the full run of the course (first session →
                    last possible session).  Used as the projection window.
recurrence          When sessions recur — cron expression or a single date.
time_slot           Start and end time of each session (same for all occurrences
                    unless an occurrence is individually rescheduled).
rate                Per-session rate charged to students.  Overrides any default.
required_instruments
                    Instruments students must bring to sessions.
capacity            Maximum number of students.  None means unlimited.
skill_range         Acceptable student skill levels for enrollment.  None means
                    open to all levels.
status              "draft" | "active" | "completed" | "cancelled"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from backend.app.domain.value_objects.financial.money import Money
from backend.app.domain.value_objects.financial.rate import Rate
from backend.app.domain.value_objects.lesson.instrument import Instrument
from backend.app.domain.value_objects.lesson.teachable_range import TeachableRange
from backend.app.domain.value_objects.scheduling.date_range import DateRange
from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
from backend.app.domain.value_objects.scheduling.time_slot import TimeSlot

VALID_STATUSES = frozenset({"draft", "active", "completed", "cancelled"})


@dataclass
class CourseEntity:
    course_id:            str
    name:                 str
    room_id:              str
    instructor_ids:       list[str]
    student_ids:          list[str]
    period:               DateRange
    recurrence:           RecurrenceRule
    time_slot:            TimeSlot
    rate:                 Optional[Rate] = None
    required_instruments: list[Instrument] = field(default_factory=list)
    capacity:             Optional[int] = None
    skill_range:          Optional[TeachableRange] = None
    description:          Optional[str] = None
    status:               str = "draft"

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"status must be one of {sorted(VALID_STATUSES)}, got {self.status!r}"
            )
        if not self.instructor_ids:
            raise ValueError("CourseEntity must have at least one instructor.")

    # ── Convenience ───────────────────────────────────────────────────────────

    @property
    def lead_instructor_id(self) -> str:
        """The primary instructor (index 0)."""
        return self.instructor_ids[0]

    @property
    def is_full(self) -> bool:
        """True if the roster has reached the capacity limit."""
        if self.capacity is None:
            return False
        return len(self.student_ids) >= self.capacity

    def accepts_skill_level(self, level) -> bool:
        """True if the student's skill level is within the course's skill range."""
        if self.skill_range is None:
            return True
        return self.skill_range.includes(level)

    # ── Serialisation ─────────────────────────────────────────────────────────

    @classmethod
    def from_dict(cls, d: dict) -> "CourseEntity":
        raw_rate = d.get("rate")
        raw_skill = d.get("skill_range")
        return cls(
            course_id=d["course_id"],
            name=d["name"],
            room_id=d["room_id"],
            instructor_ids=list(d.get("instructor_ids", [])),
            student_ids=list(d.get("student_ids", [])),
            period=DateRange(
                period_start=d["period_start"],
                period_end=d["period_end"],
            ),
            recurrence=RecurrenceRule.from_str(d["recurrence"]),
            time_slot=TimeSlot(
                start_time=d["start_time"],
                end_time=d["end_time"],
            ),
            rate=(
                Rate.from_dict(raw_rate) if isinstance(raw_rate, dict)
                else Rate.one_time(Money.of(raw_rate)) if raw_rate is not None
                else None
            ),
            required_instruments=[
                Instrument.from_dict(i) for i in d.get("required_instruments", [])
            ],
            capacity=d.get("capacity"),
            skill_range=TeachableRange.from_dict(raw_skill) if raw_skill else None,
            description=d.get("description"),
            status=d.get("status", "draft"),
        )

    def to_dict(self) -> dict:
        return {
            "course_id":            self.course_id,
            "name":                 self.name,
            "description":          self.description,
            "room_id":              self.room_id,
            "instructor_ids":       list(self.instructor_ids),
            "student_ids":          list(self.student_ids),
            "period_start":         self.period.period_start,
            "period_end":           self.period.period_end,
            "recurrence":           self.recurrence.value,
            "start_time":           self.time_slot.start_time,
            "end_time":             self.time_slot.end_time,
            "rate":                 self.rate.to_dict() if self.rate else None,
            "required_instruments": [i.to_dict() for i in self.required_instruments],
            "capacity":             self.capacity,
            "skill_range":          self.skill_range.to_dict() if self.skill_range else None,
            "status":               self.status,
        }
