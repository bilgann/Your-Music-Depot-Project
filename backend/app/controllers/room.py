from flask import Blueprint, request, jsonify

from backend.app.contracts.response import ResponseContract
from backend.app.contracts.validation import error_response, validate
import backend.app.services.room as svc

room_bp = Blueprint("rooms", __name__, url_prefix="/api/rooms")


@room_bp.route("", methods=["GET"])
def list_rooms():
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_all_rooms()).to_dict()), 200
    except Exception as e:
        return error_response(e)


@room_bp.route("/<room_id>", methods=["GET"])
def get_room(room_id):
    try:
        data = svc.get_room_by_id(room_id)
        if not data:
            return jsonify(ResponseContract(False, "Room not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@room_bp.route("", methods=["POST"])
def create_room():
    try:
        body = request.get_json()
        validate(body, "room")
        return jsonify(ResponseContract(True, "Room created.", svc.create_room(body)).to_dict()), 201
    except Exception as e:
        return error_response(e)


@room_bp.route("/<room_id>", methods=["PUT"])
def update_room(room_id):
    try:
        body = request.get_json()
        validate(body, "room", partial=True)
        return jsonify(ResponseContract(True, "Room updated.", svc.update_room(room_id, body)).to_dict()), 200
    except Exception as e:
        return error_response(e)


@room_bp.route("/<room_id>", methods=["DELETE"])
def delete_room(room_id):
    try:
        svc.delete_room(room_id)
        return jsonify(ResponseContract(True, "Room deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
