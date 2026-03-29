"""
CompatibilityVerdict constants.

Verdicts are stored on InstructorStudentCompatibilityEntity and drive the
CompatibilityService's decision logic.

Hard constraints (CompatibilityService returns can_assign=False / enforced match):
  BLOCKED  — never assign this pair (student refuses, instructor refuses, safeguarding)
  REQUIRED — only assign this instructor to this student (long-term relationship, etc.)

Soft signals (can_assign=True, but booking/ranking logic uses these as hints):
  DISLIKED  — avoid if alternatives exist
  PREFERRED — favour when alternatives exist
"""

BLOCKED   = "blocked"
DISLIKED  = "disliked"
PREFERRED = "preferred"
REQUIRED  = "required"

HARD_CONSTRAINTS: frozenset[str] = frozenset({BLOCKED, REQUIRED})
SOFT_SIGNALS:     frozenset[str] = frozenset({DISLIKED, PREFERRED})
ALL_VERDICTS:     frozenset[str] = frozenset({BLOCKED, DISLIKED, PREFERRED, REQUIRED})
