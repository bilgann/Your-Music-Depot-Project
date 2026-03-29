"""
CompatibilityResult value object.

Returned by CompatibilityService.check().  Immutable summary of whether and
why an instructor-student pairing is permitted.

Fields
------
can_assign    True unless a hard block or unmet requirement prevents assignment.
hard_verdict  "blocked" or "required" when a pair override applies; None otherwise.
soft_verdict  "preferred" or "disliked" when a soft pair override applies; None otherwise.
reasons       Human-readable explanations (empty tuple when fully compatible with no overrides).
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.domain.value_objects.compatibility.compatibility_verdict import (
    BLOCKED,
    REQUIRED,
)


@dataclass(frozen=True)
class CompatibilityResult:
    can_assign:   bool
    hard_verdict: str | None          # "blocked" | "required" | None
    soft_verdict: str | None          # "preferred" | "disliked" | None
    reasons:      tuple[str, ...]     # frozen — use tuple, not list

    # ── Convenience properties ─────────────────────────────────────────────

    @property
    def is_hard_blocked(self) -> bool:
        return self.hard_verdict == BLOCKED

    @property
    def is_hard_required(self) -> bool:
        return self.hard_verdict == REQUIRED

    # ── Factories ─────────────────────────────────────────────────────────

    @classmethod
    def ok(
        cls,
        hard_verdict: str | None = None,
        soft_verdict: str | None = None,
        reasons: tuple[str, ...] = (),
    ) -> "CompatibilityResult":
        """Pairing is allowed (may still carry soft signals or a REQUIRED hard verdict)."""
        return cls(
            can_assign=True,
            hard_verdict=hard_verdict,
            soft_verdict=soft_verdict,
            reasons=reasons,
        )

    @classmethod
    def blocked(cls, *reasons: str) -> "CompatibilityResult":
        """Pairing is hard-blocked."""
        return cls(
            can_assign=False,
            hard_verdict=BLOCKED,
            soft_verdict=None,
            reasons=reasons,
        )

    @classmethod
    def requirement_not_met(cls, *reasons: str) -> "CompatibilityResult":
        """Pairing is blocked due to an unmet student requirement or instructor restriction."""
        return cls(
            can_assign=False,
            hard_verdict=None,
            soft_verdict=None,
            reasons=reasons,
        )
