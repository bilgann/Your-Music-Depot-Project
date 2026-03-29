from dataclasses import dataclass

from backend.app.domain.exceptions.exceptions import ValidationError


@dataclass(frozen=True)
class LessonStatus:
    """Valid states a lesson can be in."""
    value: str

    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    VALID: frozenset = frozenset({"scheduled", "completed", "cancelled"})

    def __post_init__(self):
        if self.value not in self.VALID:
            raise ValidationError([{
                "field": "status",
                "message": f"Invalid lesson status '{self.value}'. Must be one of: {', '.join(sorted(self.VALID))}.",
            }])

    def __str__(self) -> str:
        return self.value
