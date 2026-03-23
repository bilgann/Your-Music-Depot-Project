from flask import Blueprint, request, jsonify

from backend.app.contracts.response import ResponseContract
import backend.app.services.room as svc

room_bp = Blueprint("rooms", __name__, url_prefix="/api/rooms")


@room_bp.route("", methods=["GET"])
def list_rooms():
    try:
        data = svc.get_all_rooms()
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@room_bp.route("/<room_id>", methods=["GET"])
def get_room(room_id):
    try:
        data = svc.get_room_by_id(room_id)
        if not data:
            return jsonify(ResponseContract(False, "Room not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@room_bp.route("", methods=["POST"])
def create_room():
    try:
        data = svc.create_room(request.get_json())
        return jsonify(ResponseContract(True, "Room created.", data).to_dict()), 201
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@room_bp.route("/<room_id>", methods=["PUT"])
def update_room(room_id):
    try:
        data = svc.update_room(room_id, request.get_json())
        return jsonify(ResponseContract(True, "Room updated.", data).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@room_bp.route("/<room_id>", methods=["DELETE"])
def delete_room(room_id):
    try:
        svc.delete_room(room_id)
        return jsonify(ResponseContract(True, "Room deleted.").to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500