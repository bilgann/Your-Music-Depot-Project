from flask import Blueprint, g, request, jsonify

from backend.app.api.dtos.auth_middleware import require_auth
from backend.app.api.dtos.response import ResponseContract
from backend.app.api.dtos.validation import error_response, validate
import backend.app.application.services.student as svc
import backend.app.application.services.audit as audit

student_bp = Blueprint("students", __name__, url_prefix="/api/students")


@student_bp.route("", methods=["GET"])
@require_auth
def list_students():
    try:
        page      = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
        search    = request.args.get("search", "").strip() or None
        data, total = svc.list_students(page, page_size, search)
        return jsonify(ResponseContract(True, "OK", data, total=total).to_dict()), 200
    except Exception as e:
        return error_response(e)


@student_bp.route("/<student_id>", methods=["GET"])
@require_auth
def get_student(student_id):
    try:
        data = svc.get_student_by_id(student_id)
        if not data:
            return jsonify(ResponseContract(False, "Student not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@student_bp.route("", methods=["POST"])
@require_auth
def create_student():
    try:
        body = request.get_json()
        validate(body, "student")
        result = svc.create_student(body)
        audit.log(g.user.id, "CREATE", "student",
                  result[0].get("student_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "Student created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@student_bp.route("/<student_id>", methods=["PUT"])
@require_auth
def update_student(student_id):
    try:
        body = request.get_json()
        validate(body, "student", partial=True)
        result = svc.update_student(student_id, body)
        audit.log(g.user.id, "UPDATE", "student", student_id, None, body)
        return jsonify(ResponseContract(True, "Student updated.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@student_bp.route("/<student_id>", methods=["DELETE"])
@require_auth
def delete_student(student_id):
    try:
        svc.delete_student(student_id)
        audit.log(g.user.id, "DELETE", "student", student_id)
        return jsonify(ResponseContract(True, "Student deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)


@student_bp.route("/<student_id>/lessons", methods=["GET"])
@require_auth
def get_student_lessons(student_id):
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_student_lessons(student_id)).to_dict()), 200
    except Exception as e:
        return error_response(e)


@student_bp.route("/<student_id>/invoices", methods=["GET"])
@require_auth
def get_student_invoices(student_id):
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_student_invoices(student_id)).to_dict()), 200
    except Exception as e:
        return error_response(e)
