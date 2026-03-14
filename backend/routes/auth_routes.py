from flask import Blueprint, request, jsonify

from backend.repositories.lesson_repository import get_lessons_for_week
from backend.services.lesson_service import create_lesson

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def get_lessons():
    week_start = request.args.get("weekStart")
    lessons = get_lessons_for_week(week_start)
    return jsonify(lessons)

@auth_bp.route("/logout", methods=["Delete"])
def schedule_lesson():
    data = request.json
    lesson = create_lesson(data)
    return jsonify(lesson)