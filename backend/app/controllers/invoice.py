from flask import Blueprint, request, jsonify

from backend.app.contracts.response import ResponseContract
import backend.app.services.invoice as svc

invoice_bp = Blueprint("invoices", __name__, url_prefix="/api/invoices")


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