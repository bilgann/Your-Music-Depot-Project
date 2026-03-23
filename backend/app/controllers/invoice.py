from flask import Blueprint, request, jsonify

from backend.app.contracts.errors import ValidationError
from backend.app.contracts.response import ResponseContract
from backend.app.contracts.validation import error_response, validate
import backend.app.services.invoice as svc

invoice_bp = Blueprint("invoices", __name__, url_prefix="/api/invoices")


# ── Static routes must come before /<invoice_id> ─────────────────────────────

@invoice_bp.route("/generate", methods=["POST"])
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
        return jsonify(ResponseContract(True, "Invoice generated.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@invoice_bp.route("/outstanding-balance", methods=["GET"])
def outstanding_balance():
    """GET /api/invoices/outstanding-balance"""
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_outstanding_balance()).to_dict()), 200
    except Exception as e:
        return error_response(e)


# ── CRUD ──────────────────────────────────────────────────────────────────────

@invoice_bp.route("", methods=["GET"])
def list_invoices():
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_all_invoices()).to_dict()), 200
    except Exception as e:
        return error_response(e)


@invoice_bp.route("/<invoice_id>", methods=["GET"])
def get_invoice(invoice_id):
    try:
        data = svc.get_invoice_by_id(invoice_id)
        if not data:
            return jsonify(ResponseContract(False, "Invoice not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@invoice_bp.route("/<invoice_id>/line-items", methods=["GET"])
def get_line_items(invoice_id):
    """GET /api/invoices/<invoice_id>/line-items"""
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_line_items(invoice_id)).to_dict()), 200
    except Exception as e:
        return error_response(e)


@invoice_bp.route("", methods=["POST"])
def create_invoice():
    try:
        body = request.get_json()
        validate(body, "invoice")
        return jsonify(ResponseContract(True, "Invoice created.", svc.create_invoice(body)).to_dict()), 201
    except Exception as e:
        return error_response(e)


@invoice_bp.route("/<invoice_id>", methods=["PUT"])
def update_invoice(invoice_id):
    try:
        body = request.get_json()
        validate(body, "invoice", partial=True)
        return jsonify(ResponseContract(True, "Invoice updated.", svc.update_invoice(invoice_id, body)).to_dict()), 200
    except Exception as e:
        return error_response(e)


@invoice_bp.route("/<invoice_id>", methods=["DELETE"])
def delete_invoice(invoice_id):
    try:
        svc.delete_invoice(invoice_id)
        return jsonify(ResponseContract(True, "Invoice deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
