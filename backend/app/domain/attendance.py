"""
Attendance policy domain rules.

Defines what charge types are valid and validates policy data before
it is persisted.  No database access — pure business rules only.
"""

from backend.app.common.base import ValidationError

VALID_CHARGE_TYPES = {"none", "flat", "percentage"}

_POLICY_CHARGE_KEYS = (
    "absent_charge_type",
    "cancel_charge_type",
    "late_cancel_charge_type",
)


def validate_policy_data(data: dict, partial: bool = False) -> None:
    """
    Raise ValidationError if any charge_type field contains an unsupported value.

    Set partial=True for PATCH-style updates where missing keys are allowed.
    """
    errors = []
    for key in _POLICY_CHARGE_KEYS:
        if key in data and data[key] not in VALID_CHARGE_TYPES:
            errors.append({
                "field": key,
                "message": f"Must be one of: {', '.join(sorted(VALID_CHARGE_TYPES))}.",
            })
    if errors:
        raise ValidationError(errors)
