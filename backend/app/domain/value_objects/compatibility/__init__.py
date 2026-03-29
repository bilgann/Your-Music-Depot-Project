from backend.app.domain.value_objects.compatibility.compatibility_result import CompatibilityResult
from backend.app.domain.value_objects.compatibility.compatibility_verdict import (
    ALL_VERDICTS,
    BLOCKED,
    DISLIKED,
    HARD_CONSTRAINTS,
    PREFERRED,
    REQUIRED,
    SOFT_SIGNALS,
)
from backend.app.domain.value_objects.compatibility.teaching_requirement import TeachingRequirement

__all__ = [
    "TeachingRequirement",
    "CompatibilityResult",
    "BLOCKED",
    "DISLIKED",
    "PREFERRED",
    "REQUIRED",
    "HARD_CONSTRAINTS",
    "SOFT_SIGNALS",
    "ALL_VERDICTS",
]
