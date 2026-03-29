from backend.app.domain.attendance import validate_policy_data
from backend.app.exceptions.base import NotFoundError, ValidationError
from backend.app.models.attendance_policy import AttendancePolicy


def get_all_policies():
    return AttendancePolicy.get_all()


def get_policy_by_id(policy_id):
    return AttendancePolicy.get(policy_id)


def get_default_policy():
    return AttendancePolicy.get_default()


def create_policy(data):
    validate_policy_data(data)
    return AttendancePolicy.create(data)


def update_policy(policy_id, data):
    rows = AttendancePolicy.get(policy_id)
    if not rows:
        raise NotFoundError("Attendance policy not found.")
    validate_policy_data(data, partial=True)
    return AttendancePolicy.update(policy_id, data)


def delete_policy(policy_id):
    rows = AttendancePolicy.get(policy_id)
    if not rows:
        raise NotFoundError("Attendance policy not found.")
    if rows[0].get("is_default"):
        raise ValidationError([{"field": "is_default", "message": "Cannot delete the default policy."}])
    return AttendancePolicy.delete(policy_id)
