from flask import Blueprint, request, jsonify

from backend.app.contracts.response import ResponseContract
from backend.app.contracts.validation import error_response, validate
import backend.app.services.student as svc

student_bp = Blueprint("students", __name__, url_prefix="/api/students")


@student_bp.route("", methods=["GET"])
def list_students():
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_all_students()).to_dict()), 200
    except Exception as e:
        return error_response(e)


@student_bp.route("/<student_id>", methods=["GET"])
def get_student(student_id):
    try:
        data = svc.get_student_by_id(student_id)
        if not data:
            return jsonify(ResponseContract(False, "Student not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@student_bp.route("", methods=["POST"])
def create_student():
    try:
        body = request.get_json()
        validate(body, "student")
        return jsonify(ResponseContract(True, "Student created.", svc.create_student(body)).to_dict()), 201
    except Exception as e:
        return error_response(e)


@student_bp.route("/<student_id>", methods=["PUT"])
def update_student(student_id):
    try:
        body = request.get_json()
        validate(body, "student", partial=True)
        return jsonify(ResponseContract(True, "Student updated.", svc.update_student(student_id, body)).to_dict()), 200
    except Exception as e:
        return error_response(e)


@student_bp.route("/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    try:
        svc.delete_student(student_id)
        return jsonify(ResponseContract(True, "Student deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
