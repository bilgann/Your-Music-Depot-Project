from flask import Blueprint, g, request, jsonify

from backend.app.contracts.auth_middleware import require_auth, require_admin
from backend.app.contracts.response import ResponseContract
from backend.app.contracts.validation import error_response
import backend.app.services.attendance_policy as svc
import backend.app.services.audit as audit

attendance_policy_bp = Blueprint("attendance_policies", __name__,
                                  url_prefix="/api/attendance-policies")

VALID_STATUSES = {"Present", "Absent", "Late Cancel", "Excused"}


@attendance_policy_bp.route("", methods=["GET"])
@require_auth
def list_policies():
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_all_policies()).to_dict()), 200
    except Exception as e:
        return error_response(e)


@attendance_policy_bp.route("/default", methods=["GET"])
@require_auth
def get_default():
    try:
        data = svc.get_default_policy()
        if not data:
            return jsonify(ResponseContract(False, "No default policy set.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return error_response(e)


@attendance_policy_bp.route("/<policy_id>", methods=["GET"])
@require_auth
def get_policy(policy_id):
    try:
        data = svc.get_policy_by_id(policy_id)
        if not data:
            return jsonify(ResponseContract(False, "Policy not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@attendance_policy_bp.route("", methods=["POST"])
@require_admin
def create_policy():
    """
    POST body example:
    {
        "name": "Standard Policy",
        "absent_charge_type": "flat",
        "absent_charge_value": 10,
        "late_cancel_charge_type": "percentage",
        "late_cancel_charge_value": 50,
        "is_default": true
    }
    absent/late_cancel charge_type: "none" | "flat" | "percentage"
    """
    try:
        body = request.get_json() or {}
        if not body.get("name"):
            from backend.app.exceptions.base import ValidationError
            raise ValidationError([{"field": "name", "message": "name is required."}])
        result = svc.create_policy(body)
        audit.log(g.user.id, "CREATE", "attendance_policy",
                  result[0].get("policy_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "Policy created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@attendance_policy_bp.route("/<policy_id>", methods=["PUT"])
@require_admin
def update_policy(policy_id):
    try:
        body = request.get_json() or {}
        result = svc.update_policy(policy_id, body)
        audit.log(g.user.id, "UPDATE", "attendance_policy", policy_id, None, body)
        return jsonify(ResponseContract(True, "Policy updated.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@attendance_policy_bp.route("/<policy_id>", methods=["DELETE"])
@require_admin
def delete_policy(policy_id):
    try:
        svc.delete_policy(policy_id)
        audit.log(g.user.id, "DELETE", "attendance_policy", policy_id)
        return jsonify(ResponseContract(True, "Policy deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
