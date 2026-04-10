from flask import Blueprint, g, request, jsonify

from backend.app.api.middleware.auth import require_admin, require_auth
from backend.app.api.contracts.response import ResponseContract
from backend.app.api.contracts.validation import error_response, validate
import backend.app.application.services.compatibility as svc
import backend.app.application.services.audit as audit

compatibility_bp = Blueprint("compatibility", __name__, url_prefix="/api/compatibility")


@compatibility_bp.route("/check", methods=["GET"])
@require_auth
def check_compatibility():
    """GET /api/compatibility/check?student_id=x&instructor_id=y"""
    try:
        student_id    = request.args.get("student_id")
        instructor_id = request.args.get("instructor_id")
        from backend.app.domain.exceptions.exceptions import ValidationError
        errors = []
        if not student_id:
            errors.append({"field": "student_id", "message": "student_id is required."})
        if not instructor_id:
            errors.append({"field": "instructor_id", "message": "instructor_id is required."})
        if errors:
            raise ValidationError(errors)
        result = svc.check_compatibility(student_id, instructor_id)
        return jsonify(ResponseContract(True, "OK", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@compatibility_bp.route("/instructors", methods=["GET"])
@require_auth
def compatible_instructors():
    """GET /api/compatibility/instructors?student_id=x"""
    try:
        student_id = request.args.get("student_id")
        if not student_id:
            from backend.app.domain.exceptions.exceptions import ValidationError
            raise ValidationError([{"field": "student_id", "message": "student_id is required."}])
        result = svc.filter_compatible_instructors(student_id)
        return jsonify(ResponseContract(True, "OK", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@compatibility_bp.route("/students", methods=["GET"])
@require_auth
def compatible_students():
    """GET /api/compatibility/students?instructor_id=x"""
    try:
        instructor_id = request.args.get("instructor_id")
        if not instructor_id:
            from backend.app.domain.exceptions.exceptions import ValidationError
            raise ValidationError([{"field": "instructor_id", "message": "instructor_id is required."}])
        result = svc.filter_compatible_students(instructor_id)
        return jsonify(ResponseContract(True, "OK", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@compatibility_bp.route("", methods=["POST"])
@require_admin
def set_compatibility():
    """POST /api/compatibility  —  create or update a pair override."""
    try:
        body = request.get_json()
        validate(body, "compatibility")
        result = svc.set_compatibility(body)
        audit.log(g.user.user_id, "UPSERT", "instructor_student_compatibility", None, None, body)
        return jsonify(ResponseContract(True, "Compatibility override saved.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@compatibility_bp.route("/<compatibility_id>", methods=["DELETE"])
@require_admin
def delete_compatibility(compatibility_id):
    try:
        svc.delete_compatibility(compatibility_id)
        audit.log(g.user.user_id, "DELETE", "instructor_student_compatibility", compatibility_id)
        return jsonify(ResponseContract(True, "Compatibility override deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
