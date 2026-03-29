"""
Compatibility domain error codes and default messages.

Covers instructor-student pairing failures surfaced by CompatibilityService.
"""

INSTRUCTOR_BLOCKED              = "INSTRUCTOR_BLOCKED"
INSTRUCTOR_REQUIREMENT_NOT_MET  = "INSTRUCTOR_REQUIREMENT_NOT_MET"
INSTRUCTOR_RESTRICTION_VIOLATED = "INSTRUCTOR_RESTRICTION_VIOLATED"

MESSAGES: dict[str, str] = {
    INSTRUCTOR_BLOCKED:              "This instructor cannot be assigned to this student.",
    INSTRUCTOR_REQUIREMENT_NOT_MET:  "The instructor does not meet the student's required credentials.",
    INSTRUCTOR_RESTRICTION_VIOLATED: "The student does not meet the instructor's teaching restrictions.",
}
