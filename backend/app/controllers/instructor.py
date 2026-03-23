from flask import Blueprint, request, jsonify

from backend.app.contracts.response import ResponseContract
from backend.app.contracts.validation import error_response, validate
import backend.app.services.instructor as svc

instructor_bp = Blueprint("instructors", __name__, url_prefix="/api/instructors")


@instructor_bp.route("", methods=["GET"])
def list_instructors():
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_all_instructors()).to_dict()), 200
    except Exception as e:
        return error_response(e)


@instructor_bp.route("/<instructor_id>", methods=["GET"])
def get_instructor(instructor_id):
    try:
        data = svc.get_instructor_by_id(instructor_id)
        if not data:
            return jsonify(ResponseContract(False, "Instructor not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@instructor_bp.route("", methods=["POST"])
def create_instructor():
    try:
        body = request.get_json()
        validate(body, "instructor")
        return jsonify(ResponseContract(True, "Instructor created.", svc.create_instructor(body)).to_dict()), 201
    except Exception as e:
        return error_response(e)


@instructor_bp.route("/<instructor_id>", methods=["PUT"])
def update_instructor(instructor_id):
    try:
        body = request.get_json()
        validate(body, "instructor", partial=True)
        return jsonify(ResponseContract(True, "Instructor updated.", svc.update_instructor(instructor_id, body)).to_dict()), 200
    except Exception as e:
        return error_response(e)


@instructor_bp.route("/<instructor_id>", methods=["DELETE"])
def delete_instructor(instructor_id):
    try:
        svc.delete_instructor(instructor_id)
        return jsonify(ResponseContract(True, "Instructor deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
