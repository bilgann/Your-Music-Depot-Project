from flask import Blueprint, request, jsonify

from backend.app.contracts.auth_middleware import require_admin
from backend.app.contracts.response import ResponseContract
from backend.app.contracts.validation import error_response
from backend.app.models.audit import AuditLog

audit_bp = Blueprint("audit", __name__, url_prefix="/api/audit")


@audit_bp.route("", methods=["GET"])
@require_admin
def list_audit_logs():
    """
    GET /api/audit
    Optional query params:
      ?entity_type=lesson    — filter by entity type
      ?entity_id=<id>        — filter by specific record ID
      ?limit=100             — max rows returned (default 200)
    """
    try:
        entity_type = request.args.get("entity_type")
        entity_id = request.args.get("entity_id")
        limit = min(int(request.args.get("limit", 200)), 500)

        data = AuditLog.list_filtered(entity_type=entity_type, entity_id=entity_id, limit=limit)
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return error_response(e)
