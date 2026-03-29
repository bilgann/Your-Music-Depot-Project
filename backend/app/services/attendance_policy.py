from backend.app.exceptions.base import NotFoundError, ValidationError
from backend.app.models.attendance_policy import AttendancePolicy, VALID_CHARGE_TYPES


def get_all_policies():
    return AttendancePolicy.get_all()


def get_policy_by_id(policy_id):
    return AttendancePolicy.get(policy_id)


def get_default_policy():
    return AttendancePolicy.get_default()


def create_policy(data):
    _validate_policy_data(data)
    return AttendancePolicy.create(data)


def update_policy(policy_id, data):
    rows = AttendancePolicy.get(policy_id)
    if not rows:
        raise NotFoundError("Attendance policy not found.")
    _validate_policy_data(data, partial=True)
    return AttendancePolicy.update(policy_id, data)


def delete_policy(policy_id):
    rows = AttendancePolicy.get(policy_id)
    if not rows:
        raise NotFoundError("Attendance policy not found.")
    if rows[0].get("is_default"):
        raise ValidationError([{"field": "is_default", "message": "Cannot delete the default policy."}])
    return AttendancePolicy.delete(policy_id)


def _validate_policy_data(data: dict, partial: bool = False):
    errors = []
    for key in ("absent_charge_type", "cancel_charge_type", "late_cancel_charge_type"):
        if key in data and data[key] not in VALID_CHARGE_TYPES:
            errors.append({"field": key, "message": f"Must be one of: {', '.join(VALID_CHARGE_TYPES)}."})
    if errors:
        raise ValidationError(errors)
