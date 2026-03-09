# defines API endpoints

from flask import Blueprint, request, jsonify
from services.scheduling_service import create_lesson, get_lessons_by_teacher, get_lessons_for_week

lesson_bp = Blueprint('lessons', __name__)

@lesson_bp.route('/lessons', methods=['GET'])
def get_lessons():
    week_start = request.args.get("weekStart")
    lessons = get_lessons_for_week(week_start)
    return jsonify(lessons)

@lesson_bp.route("/lessons", methods=["POST"])
def schedule_lesson():
    data = request.json
    lesson = create_lesson(data)
    return jsonify(lesson)