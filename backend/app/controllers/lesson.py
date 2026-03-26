from flask import Blueprint, g, request, jsonify

from backend.app.contracts.auth_middleware import require_auth
from backend.app.contracts.response import ResponseContract
from backend.app.contracts.validation import error_response, validate
import backend.app.services.lesson as svc
import backend.app.services.audit as audit

lesson_bp = Blueprint("lessons", __name__, url_prefix="/api/lessons")


@lesson_bp.route("", methods=["GET"])
@require_auth
def list_lessons():
    try:
        week_start = request.args.get("weekStart")
        week_end = request.args.get("weekEnd")
        data = (
            svc.get_lessons_for_week(week_start, week_end)
            if week_start and week_end
            else svc.get_all_lessons()
        )
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return error_response(e)


@lesson_bp.route("/<lesson_id>", methods=["GET"])
@require_auth
def get_lesson(lesson_id):
    try:
        data = svc.get_lesson_by_id(lesson_id)
        if not data:
            return jsonify(ResponseContract(False, "Lesson not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@lesson_bp.route("", methods=["POST"])
@require_auth
def create_lesson():
    try:
        body = request.get_json()
        validate(body, "lesson")
        result = svc.create_lesson(body)
        audit.log(g.user.id, "CREATE", "lesson",
                  result[0].get("lesson_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "Lesson created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@lesson_bp.route("/<lesson_id>", methods=["PUT"])
@require_auth
def update_lesson(lesson_id):
    try:
        body = request.get_json()
        validate(body, "lesson", partial=True)
        result = svc.update_lesson(lesson_id, body)
        audit.log(g.user.id, "UPDATE", "lesson", lesson_id, None, body)
        return jsonify(ResponseContract(True, "Lesson updated.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@lesson_bp.route("/<lesson_id>", methods=["DELETE"])
@require_auth
def delete_lesson(lesson_id):
    try:
        svc.delete_lesson(lesson_id)
        audit.log(g.user.id, "DELETE", "lesson", lesson_id)
        return jsonify(ResponseContract(True, "Lesson deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
