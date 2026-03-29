from flask import Blueprint, g, request, jsonify

from backend.app.api.middleware.auth import require_admin, require_auth
from backend.app.api.contracts.response import ResponseContract
from backend.app.api.contracts.validation import error_response, validate
import backend.app.application.services.credential as svc
import backend.app.application.services.audit as audit

credential_bp = Blueprint("credentials", __name__, url_prefix="/api/credentials")


@credential_bp.route("", methods=["GET"])
@require_auth
def list_credentials():
    try:
        instructor_id = request.args.get("instructor_id")
        active_only   = request.args.get("active", "").lower() == "true"
        if instructor_id and active_only:
            data = svc.get_active_credentials_by_instructor(instructor_id)
        elif instructor_id:
            data = svc.get_credentials_by_instructor(instructor_id)
        else:
            data = svc.get_all_credentials()
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return error_response(e)


@credential_bp.route("/<credential_id>", methods=["GET"])
@require_auth
def get_credential(credential_id):
    try:
        data = svc.get_credential_by_id(credential_id)
        if not data:
            return jsonify(ResponseContract(False, "Credential not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@credential_bp.route("", methods=["POST"])
@require_admin
def create_credential():
    try:
        body = request.get_json()
        validate(body, "credential")
        result = svc.create_credential(body)
        audit.log(g.user.id, "CREATE", "credential",
                  result[0].get("credential_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "Credential created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@credential_bp.route("/<credential_id>", methods=["PUT"])
@require_admin
def update_credential(credential_id):
    try:
        body = request.get_json()
        validate(body, "credential", partial=True)
        result = svc.update_credential(credential_id, body)
        audit.log(g.user.id, "UPDATE", "credential", credential_id, None, body)
        return jsonify(ResponseContract(True, "Credential updated.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@credential_bp.route("/<credential_id>", methods=["DELETE"])
@require_admin
def delete_credential(credential_id):
    try:
        svc.delete_credential(credential_id)
        audit.log(g.user.id, "DELETE", "credential", credential_id)
        return jsonify(ResponseContract(True, "Credential deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
