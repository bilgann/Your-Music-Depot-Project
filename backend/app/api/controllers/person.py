from flask import Blueprint, g, request, jsonify

from backend.app.api.middleware.auth import require_auth
from backend.app.api.contracts.response import ResponseContract
from backend.app.api.contracts.validation import error_response, validate
import backend.app.application.services.person as svc
import backend.app.application.services.audit as audit

person_bp = Blueprint("persons", __name__, url_prefix="/api/persons")


@person_bp.route("", methods=["GET"])
@require_auth
def list_persons():
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_all_persons()).to_dict()), 200
    except Exception as e:
        return error_response(e)


@person_bp.route("/<person_id>", methods=["GET"])
@require_auth
def get_person(person_id):
    try:
        data = svc.get_person_by_id(person_id)
        if not data:
            return jsonify(ResponseContract(False, "Person not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@person_bp.route("", methods=["POST"])
@require_auth
def create_person():
    try:
        body = request.get_json()
        validate(body, "person")
        result = svc.create_person(body)
        audit.log(g.user.user_id, "CREATE", "person",
                  result[0].get("person_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "Person created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@person_bp.route("/<person_id>", methods=["PUT"])
@require_auth
def update_person(person_id):
    try:
        body = request.get_json()
        validate(body, "person", partial=True)
        result = svc.update_person(person_id, body)
        audit.log(g.user.user_id, "UPDATE", "person", person_id, None, body)
        return jsonify(ResponseContract(True, "Person updated.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@person_bp.route("/<person_id>", methods=["DELETE"])
@require_auth
def delete_person(person_id):
    try:
        svc.delete_person(person_id)
        audit.log(g.user.user_id, "DELETE", "person", person_id)
        return jsonify(ResponseContract(True, "Person deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
