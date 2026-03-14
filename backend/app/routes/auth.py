import logging
from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)
validUser = "barns"
validPassword = "somePassword"

logging.basicConfig(
    filename='responses.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@auth_bp.route('/login', methods=['GET'])
def login():
    username = request.args.get("username")
    password = request.args.get("password")
    jsonify = get_lessons_for_week(week_start)
    return jsonify(lessons)

@auth_bp.route("/logout", methods=["Delete"])
def logout():
    data = request.json
    lesson = create_lesson(data)
    return jsonify(lesson)