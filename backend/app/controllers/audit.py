from flask import Blueprint, request, jsonify

from backend.app.contracts.auth_middleware import require_admin
from backend.app.contracts.response import ResponseContract
from backend.app.contracts.validation import error_response
from backend.app.singletons.database import DatabaseConnection

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

        db = DatabaseConnection().client
        query = db.table("audit_log").select("*").order("created_at", desc=True).limit(limit)

        if entity_type:
            query = query.eq("entity_type", entity_type)
        if entity_id:
            query = query.eq("entity_id", entity_id)

        data = query.execute().data
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return error_response(e)
