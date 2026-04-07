from dataclasses import dataclass, field
from typing import Optional

from backend.app.domain.value_objects.financial.money import Money
from backend.app.domain.value_objects.financial.rate import Rate
from backend.app.domain.value_objects.scheduling.recurrence_rule import RecurrenceRule
from backend.app.domain.value_objects.scheduling.time_slot import TimeSlot


@dataclass
class LessonEntity:
    """A scheduled lesson template in a room with an instructor.

    student_ids  Enrolled student roster.  For private lessons this will
                 typically contain a single student_id.  The application
                 service reads this list when generating LessonEnrollmentEntity
                 records after projection.
    course_id    Optional link to a parent CourseEntity.  Set when this lesson
                 belongs to a course; None for standalone lessons.
    """
    lesson_id:     str
    instructor_id: str
    room_id:       str
    time_slot:     TimeSlot
    student_ids:   list[str] = field(default_factory=list)
    rate:          Optional[Rate] = None
    status:        Optional[str] = None
    recurrence:    Optional[RecurrenceRule] = None
    course_id:     Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "LessonEntity":
        raw_rate = d.get("rate")
        raw_rec  = d.get("recurrence")
        return cls(
            lesson_id=d["lesson_id"],
            instructor_id=d["instructor_id"],
            room_id=d["room_id"],
            time_slot=TimeSlot(
                start_time=d["start_time"],
                end_time=d["end_time"],
            ),
            student_ids=list(d.get("student_ids", [])),
            rate=Rate.one_time(Money.of(raw_rate)) if raw_rate is not None else None,
            status=d.get("status"),
            recurrence=RecurrenceRule.from_str(raw_rec) if raw_rec else None,
            course_id=d.get("course_id"),
        )

    def to_dict(self) -> dict:
        return {
            "lesson_id":     self.lesson_id,
            "course_id":     self.course_id,
            "instructor_id": self.instructor_id,
            "room_id":       self.room_id,
            "start_time":    self.time_slot.start_time,
            "end_time":      self.time_slot.end_time,
            "student_ids":   list(self.student_ids),
            "rate":          self.rate.amount.amount if self.rate else None,
            "status":        self.status,
            "recurrence":    str(self.recurrence) if self.recurrence else None,
        }
