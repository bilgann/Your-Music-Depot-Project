import sys
import os

import backend.app.services.lesson
from backend.app.services.scheduling import create_lesson

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# defines API endpoints
from flask import Blueprint, request, jsonify

lesson_bp = Blueprint('lessons', __name__)

@lesson_bp.route('/lessons', methods=['GET'])
def get_lessons():
    week_start = request.args.get("weekStart")
    lessons = backend.get_lessons_for_week(week_start)
    return jsonify(lessons)

@lesson_bp.route("/lessons", methods=["POST"])
def schedule_lesson():
    data = request.json
    lesson = create_lesson(data)
    return jsonify(lesson)