from flask import Blueprint, request, jsonify

from backend.app.contracts.response import ResponseContract
import backend.app.services.lesson as svc

lesson_bp = Blueprint("lessons", __name__, url_prefix="/api/lessons")


@lesson_bp.route("", methods=["GET"])
def list_lessons():
    try:
        week_start = request.args.get("weekStart")
        week_end = request.args.get("weekEnd")
        if week_start and week_end:
            data = svc.get_lessons_for_week(week_start, week_end)
        else:
            data = svc.get_all_lessons()
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@lesson_bp.route("/<lesson_id>", methods=["GET"])
def get_lesson(lesson_id):
    try:
        data = svc.get_lesson_by_id(lesson_id)
        if not data:
            return jsonify(ResponseContract(False, "Lesson not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@lesson_bp.route("", methods=["POST"])
def create_lesson():
    try:
        data = svc.create_lesson(request.get_json())
        return jsonify(ResponseContract(True, "Lesson created.", data).to_dict()), 201
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@lesson_bp.route("/<lesson_id>", methods=["PUT"])
def update_lesson(lesson_id):
    try:
        data = svc.update_lesson(lesson_id, request.get_json())
        return jsonify(ResponseContract(True, "Lesson updated.", data).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@lesson_bp.route("/<lesson_id>", methods=["DELETE"])
def delete_lesson(lesson_id):
    try:
        svc.delete_lesson(lesson_id)
        return jsonify(ResponseContract(True, "Lesson deleted.").to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500