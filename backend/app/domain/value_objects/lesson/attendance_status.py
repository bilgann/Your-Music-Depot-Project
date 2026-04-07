from dataclasses import dataclass

from backend.app.domain.exceptions.exceptions import ValidationError


@dataclass(frozen=True)
class AttendanceStatus:
    """Valid attendance states for a lesson enrollment."""
    value: str

    PRESENT = "present"
    ABSENT = "absent"
    CANCEL = "cancel"
    LATE_CANCEL = "late_cancel"

    VALID: frozenset = frozenset({"present", "absent", "cancel", "late_cancel"})

    # Statuses that may trigger a charge per an attendance policy
    CHARGEABLE: frozenset = frozenset({"absent", "cancel", "late_cancel"})

    def __post_init__(self):
        if self.value not in self.VALID:
            raise ValidationError([{
                "field": "attendance_status",
                "message": f"Invalid attendance status '{self.value}'. Must be one of: {', '.join(sorted(self.VALID))}.",
            }])

    def __str__(self) -> str:
        return self.value

    def is_chargeable(self) -> bool:
        return self.value in self.CHARGEABLE
