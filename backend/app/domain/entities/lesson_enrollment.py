from dataclasses import dataclass
from typing import Optional

from backend.app.domain.value_objects.lesson.attendance_status import AttendanceStatus


@dataclass
class LessonEnrollmentEntity:
    """Records a student's enrollment in a specific lesson occurrence."""
    enrollment_id: str
    occurrence_id: str
    student_id: str
    attendance_status: Optional[AttendanceStatus] = None

    @classmethod
    def from_dict(cls, d: dict) -> "LessonEnrollmentEntity":
        raw_status = d.get("attendance_status")
        return cls(
            enrollment_id=d["enrollment_id"],
            occurrence_id=d["occurrence_id"],
            student_id=d["student_id"],
            attendance_status=AttendanceStatus(raw_status) if raw_status else None,
        )

    def to_dict(self) -> dict:
        return {
            "enrollment_id": self.enrollment_id,
            "occurrence_id": self.occurrence_id,
            "student_id": self.student_id,
            "attendance_status": self.attendance_status.value if self.attendance_status else None,
        }
