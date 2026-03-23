from flask import Blueprint, request, jsonify

from backend.app.contracts.response import ResponseContract
import backend.app.services.invoice as svc

invoice_bp = Blueprint("invoices", __name__, url_prefix="/api/invoices")


# ── Static routes must come before /<invoice_id> ─────────────────────────────

@invoice_bp.route("/generate", methods=["POST"])
def generate_invoice():
    """
    POST /api/invoices/generate
    Body: { "student_id": ..., "year": ..., "month": ... }
    Generates an invoice + line items for all Completed/Scheduled lessons
    that month for the given student.
    """
    try:
        body = request.get_json()
        student_id = body.get("student_id")
        year = body.get("year")
        month = body.get("month")
        if not all([student_id, year, month]):
            return jsonify(ResponseContract(False, "student_id, year, and month are required.").to_dict()), 400
        result = svc.generate_monthly_invoice(student_id, int(year), int(month))
        return jsonify(ResponseContract(True, "Invoice generated.", result).to_dict()), 201
    except ValueError as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 422
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@invoice_bp.route("/outstanding-balance", methods=["GET"])
def outstanding_balance():
    """GET /api/invoices/outstanding-balance"""
    try:
        data = svc.get_outstanding_balance()
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


# ── CRUD ──────────────────────────────────────────────────────────────────────

@invoice_bp.route("", methods=["GET"])
def list_invoices():
    try:
        data = svc.get_all_invoices()
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@invoice_bp.route("/<invoice_id>", methods=["GET"])
def get_invoice(invoice_id):
    try:
        data = svc.get_invoice_by_id(invoice_id)
        if not data:
            return jsonify(ResponseContract(False, "Invoice not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@invoice_bp.route("/<invoice_id>/line-items", methods=["GET"])
def get_line_items(invoice_id):
    """GET /api/invoices/<invoice_id>/line-items"""
    try:
        data = svc.get_line_items(invoice_id)
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@invoice_bp.route("", methods=["POST"])
def create_invoice():
    try:
        data = svc.create_invoice(request.get_json())
        return jsonify(ResponseContract(True, "Invoice created.", data).to_dict()), 201
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@invoice_bp.route("/<invoice_id>", methods=["PUT"])
def update_invoice(invoice_id):
    try:
        data = svc.update_invoice(invoice_id, request.get_json())
        return jsonify(ResponseContract(True, "Invoice updated.", data).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@invoice_bp.route("/<invoice_id>", methods=["DELETE"])
def delete_invoice(invoice_id):
    try:
        svc.delete_invoice(invoice_id)
        return jsonify(ResponseContract(True, "Invoice deleted.").to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500