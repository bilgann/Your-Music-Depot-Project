from flask import Blueprint, g, request, jsonify

from backend.app.api.middleware.auth import require_auth
from backend.app.api.contracts.response import ResponseContract
from backend.app.api.contracts.validation import error_response, validate
import backend.app.application.services.room as svc
import backend.app.application.services.audit as audit

room_bp = Blueprint("rooms", __name__, url_prefix="/api/rooms")


@room_bp.route("", methods=["GET"])
@require_auth
def list_rooms():
    try:
        page      = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
        search    = request.args.get("search", "").strip() or None
        data, total = svc.list_rooms(page, page_size, search)
        return jsonify(ResponseContract(True, "OK", data, total=total).to_dict()), 200
    except Exception as e:
        return error_response(e)


@room_bp.route("/<room_id>", methods=["GET"])
@require_auth
def get_room(room_id):
    try:
        data = svc.get_room_by_id(room_id)
        if not data:
            return jsonify(ResponseContract(False, "Room not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@room_bp.route("", methods=["POST"])
@require_auth
def create_room():
    try:
        body = request.get_json()
        validate(body, "room")
        result = svc.create_room(body)
        audit.log(g.user.user_id, "CREATE", "room",
                  result[0].get("room_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "Room created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@room_bp.route("/<room_id>", methods=["PUT"])
@require_auth
def update_room(room_id):
    try:
        body = request.get_json()
        validate(body, "room", partial=True)
        result = svc.update_room(room_id, body)
        audit.log(g.user.user_id, "UPDATE", "room", room_id, None, body)
        return jsonify(ResponseContract(True, "Room updated.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@room_bp.route("/<room_id>", methods=["DELETE"])
@require_auth
def delete_room(room_id):
    try:
        svc.delete_room(room_id)
        audit.log(g.user.user_id, "DELETE", "room", room_id)
        return jsonify(ResponseContract(True, "Room deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
