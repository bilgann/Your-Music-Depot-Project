from flask import Blueprint, g, request, jsonify

from backend.app.api.middleware.auth import require_admin, require_auth
from backend.app.api.contracts.response import ResponseContract
from backend.app.api.contracts.validation import error_response, validate
import backend.app.application.services.school_schedule as svc
import backend.app.application.services.audit as audit

school_schedule_bp = Blueprint(
    "school_schedules", __name__, url_prefix="/api/school-schedules",
)


# ── School schedule CRUD ─────────────────────────────────────────────────────

@school_schedule_bp.route("", methods=["GET"])
@require_auth
def list_schedules():
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
        active_only = request.args.get("active_only", "").lower() == "true"
        data, total = svc.list_school_schedules(page, page_size, active_only)
        return jsonify(ResponseContract(True, "OK", data, total=total).to_dict()), 200
    except Exception as e:
        return error_response(e)


@school_schedule_bp.route("/<schedule_id>", methods=["GET"])
@require_auth
def get_schedule(schedule_id):
    try:
        data = svc.get_school_schedule_by_id(schedule_id)
        if not data:
            return jsonify(ResponseContract(False, "School schedule entry not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@school_schedule_bp.route("", methods=["POST"])
@require_admin
def create_schedule():
    try:
        body = request.get_json()
        validate(body, "school_schedule")
        result = svc.create_school_schedule(body)
        audit.log(g.user.user_id, "CREATE", "school_schedule",
                  result[0].get("schedule_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "School schedule entry created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@school_schedule_bp.route("/<schedule_id>", methods=["PUT"])
@require_admin
def update_schedule(schedule_id):
    try:
        body = request.get_json()
        validate(body, "school_schedule", partial=True)
        result = svc.update_school_schedule(schedule_id, body)
        audit.log(g.user.user_id, "UPDATE", "school_schedule", schedule_id, None, body)
        return jsonify(ResponseContract(True, "School schedule entry updated.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@school_schedule_bp.route("/<schedule_id>", methods=["DELETE"])
@require_admin
def delete_schedule(schedule_id):
    try:
        svc.delete_school_schedule(schedule_id)
        audit.log(g.user.user_id, "DELETE", "school_schedule", schedule_id)
        return jsonify(ResponseContract(True, "School schedule entry deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)


# ── Overrides ────────────────────────────────────────────────────────────────

@school_schedule_bp.route("/<schedule_id>/overrides", methods=["GET"])
@require_auth
def list_overrides(schedule_id):
    try:
        data = svc.list_overrides(schedule_id)
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return error_response(e)


@school_schedule_bp.route("/<schedule_id>/overrides", methods=["POST"])
@require_admin
def create_override(schedule_id):
    try:
        body = request.get_json()
        validate(body, "school_schedule_override")
        result = svc.create_override(schedule_id, body)
        audit.log(g.user.user_id, "CREATE", "school_schedule_override",
                  result[0].get("override_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "Override created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@school_schedule_bp.route("/<schedule_id>/overrides/<override_id>", methods=["DELETE"])
@require_admin
def delete_override(schedule_id, override_id):
    try:
        svc.delete_override(schedule_id, override_id)
        audit.log(g.user.user_id, "DELETE", "school_schedule_override", override_id)
        return jsonify(ResponseContract(True, "Override deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
