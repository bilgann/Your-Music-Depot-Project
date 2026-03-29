from flask import Blueprint, g, request, jsonify

from backend.app.api.dtos.auth_middleware import require_admin
from backend.app.common.base import ValidationError
from backend.app.api.dtos.response import ResponseContract
from backend.app.api.dtos.validation import error_response, validate
import backend.app.application.services.invoice as svc
import backend.app.application.services.audit as audit

invoice_bp = Blueprint("invoices", __name__, url_prefix="/api/invoices")


# ── Static routes must come before /<invoice_id> ─────────────────────────────

@invoice_bp.route("/generate", methods=["POST"])
@require_admin
def generate_invoice():
    """POST /api/invoices/generate  —  body: { student_id, year, month }"""
    try:
        body = request.get_json()
        if body is None:
            raise ValidationError([{"field": "_body", "message": "Request body must be JSON."}])
        errors = []
        for field in ("student_id", "year", "month"):
            if body.get(field) is None:
                errors.append({"field": field, "message": f"{field} is required."})
        if errors:
            raise ValidationError(errors)
        result = svc.generate_monthly_invoice(body["student_id"], int(body["year"]), int(body["month"]))
        audit.log(g.user.id, "CREATE", "invoice",
                  result["invoice"].get("invoice_id"), None,
                  {"student_id": body["student_id"], "year": body["year"], "month": body["month"]})
        return jsonify(ResponseContract(True, "Invoice generated.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@invoice_bp.route("/outstanding-balance", methods=["GET"])
@require_admin
def outstanding_balance():
    """GET /api/invoices/outstanding-balance?client_id=xxx"""
    try:
        client_id = request.args.get("client_id")
        return jsonify(ResponseContract(True, "OK", svc.get_outstanding_balance(client_id)).to_dict()), 200
    except Exception as e:
        return error_response(e)


# ── CRUD ──────────────────────────────────────────────────────────────────────

@invoice_bp.route("", methods=["GET"])
@require_admin
def list_invoices():
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_all_invoices()).to_dict()), 200
    except Exception as e:
        return error_response(e)


@invoice_bp.route("/<invoice_id>", methods=["GET"])
@require_admin
def get_invoice(invoice_id):
    try:
        data = svc.get_invoice_by_id(invoice_id)
        if not data:
            return jsonify(ResponseContract(False, "Invoice not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@invoice_bp.route("/<invoice_id>/line-items", methods=["GET"])
@require_admin
def get_line_items(invoice_id):
    """GET /api/invoices/<invoice_id>/line-items"""
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_line_items(invoice_id)).to_dict()), 200
    except Exception as e:
        return error_response(e)


@invoice_bp.route("", methods=["POST"])
@require_admin
def create_invoice():
    try:
        body = request.get_json()
        validate(body, "invoice")
        result = svc.create_invoice(body)
        audit.log(g.user.id, "CREATE", "invoice",
                  result[0].get("invoice_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "Invoice created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@invoice_bp.route("/<invoice_id>", methods=["PUT"])
@require_admin
def update_invoice(invoice_id):
    try:
        body = request.get_json()
        validate(body, "invoice", partial=True)
        result = svc.update_invoice(invoice_id, body)
        audit.log(g.user.id, "UPDATE", "invoice", invoice_id, None, body)
        return jsonify(ResponseContract(True, "Invoice updated.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@invoice_bp.route("/<invoice_id>", methods=["DELETE"])
@require_admin
def delete_invoice(invoice_id):
    try:
        svc.delete_invoice(invoice_id)
        audit.log(g.user.id, "DELETE", "invoice", invoice_id)
        return jsonify(ResponseContract(True, "Invoice deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
