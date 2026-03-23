from flask import Blueprint, request, jsonify

from backend.app.contracts.response import ResponseContract
import backend.app.services.instructor as svc

instructor_bp = Blueprint("instructors", __name__, url_prefix="/api/instructors")


@instructor_bp.route("", methods=["GET"])
def list_instructors():
    try:
        data = svc.get_all_instructors()
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@instructor_bp.route("/<instructor_id>", methods=["GET"])
def get_instructor(instructor_id):
    try:
        data = svc.get_instructor_by_id(instructor_id)
        if not data:
            return jsonify(ResponseContract(False, "Instructor not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@instructor_bp.route("", methods=["POST"])
def create_instructor():
    try:
        data = svc.create_instructor(request.get_json())
        return jsonify(ResponseContract(True, "Instructor created.", data).to_dict()), 201
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@instructor_bp.route("/<instructor_id>", methods=["PUT"])
def update_instructor(instructor_id):
    try:
        data = svc.update_instructor(instructor_id, request.get_json())
        return jsonify(ResponseContract(True, "Instructor updated.", data).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@instructor_bp.route("/<instructor_id>", methods=["DELETE"])
def delete_instructor(instructor_id):
    try:
        svc.delete_instructor(instructor_id)
        return jsonify(ResponseContract(True, "Instructor deleted.").to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500