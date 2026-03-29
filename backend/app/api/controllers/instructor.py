from flask import Blueprint, g, request, jsonify

from backend.app.api.dtos.auth_middleware import require_auth
from backend.app.api.dtos.response import ResponseContract
from backend.app.api.dtos.validation import error_response, validate
import backend.app.application.services.instructor as svc
import backend.app.application.services.audit as audit

instructor_bp = Blueprint("instructors", __name__, url_prefix="/api/instructors")


@instructor_bp.route("", methods=["GET"])
@require_auth
def list_instructors():
    try:
        page      = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
        search    = request.args.get("search", "").strip() or None
        data, total = svc.list_instructors(page, page_size, search)
        return jsonify(ResponseContract(True, "OK", data, total=total).to_dict()), 200
    except Exception as e:
        return error_response(e)


@instructor_bp.route("/<instructor_id>", methods=["GET"])
@require_auth
def get_instructor(instructor_id):
    try:
        data = svc.get_instructor_by_id(instructor_id)
        if not data:
            return jsonify(ResponseContract(False, "Instructor not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@instructor_bp.route("", methods=["POST"])
@require_auth
def create_instructor():
    try:
        body = request.get_json()
        validate(body, "instructor")
        result = svc.create_instructor(body)
        audit.log(g.user.id, "CREATE", "instructor",
                  result[0].get("instructor_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "Instructor created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@instructor_bp.route("/<instructor_id>", methods=["PUT"])
@require_auth
def update_instructor(instructor_id):
    try:
        body = request.get_json()
        validate(body, "instructor", partial=True)
        result = svc.update_instructor(instructor_id, body)
        audit.log(g.user.id, "UPDATE", "instructor", instructor_id, None, body)
        return jsonify(ResponseContract(True, "Instructor updated.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@instructor_bp.route("/<instructor_id>", methods=["DELETE"])
@require_auth
def delete_instructor(instructor_id):
    try:
        svc.delete_instructor(instructor_id)
        audit.log(g.user.id, "DELETE", "instructor", instructor_id)
        return jsonify(ResponseContract(True, "Instructor deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
