from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def get_lessons():
    username = request.args.get("username")
    password = request.args.get("password")
    jsonify = get_lessons_for_week(week_start)
    return jsonify(lessons)

@auth_bp.route("/logout", methods=["Delete"])
def schedule_lesson():
    data = request.json
    lesson = create_lesson(data)
    return jsonify(lesson)