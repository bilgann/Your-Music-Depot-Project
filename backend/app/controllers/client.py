from flask import Blueprint, g, request, jsonify

from backend.app.contracts.auth_middleware import require_auth
from backend.app.contracts.response import ResponseContract
from backend.app.contracts.validation import error_response, validate
from backend.app.exceptions.base import ValidationError
from backend.app.models.credit_transaction import CreditTransaction
import backend.app.services.client as svc
import backend.app.services.invoice as invoice_svc
import backend.app.services.payment as payment_svc
import backend.app.services.audit as audit

client_bp = Blueprint("clients", __name__, url_prefix="/api/clients")


@client_bp.route("", methods=["GET"])
@require_auth
def list_clients():
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_all_clients()).to_dict()), 200
    except Exception as e:
        return error_response(e)


@client_bp.route("/<client_id>", methods=["GET"])
@require_auth
def get_client(client_id):
    try:
        data = svc.get_client_by_id(client_id)
        if not data:
            return jsonify(ResponseContract(False, "Client not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@client_bp.route("/<client_id>/pay", methods=["POST"])
@require_auth
def pay_via_client(client_id):
    """POST /api/clients/<id>/pay  —  body: { amount, payment_method? }"""
    try:
        body = request.get_json() or {}
        amount = body.get("amount")
        if amount is None or float(amount) <= 0:
            raise ValidationError([{"field": "amount", "message": "amount must be greater than 0."}])
        payment_method = body.get("payment_method", "Card")
        result = payment_svc.pay_via_client(client_id, float(amount), payment_method)
        audit.log(g.user.id, "CREATE", "payment", client_id, None,
                  {"amount": amount, "payment_method": payment_method})
        return jsonify(ResponseContract(True, "Payment applied.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@client_bp.route("/<client_id>/credits", methods=["GET"])
@require_auth
def get_client_credits(client_id):
    """GET /api/clients/<id>/credits  —  balance + full transaction history."""
    try:
        data = svc.get_client_by_id(client_id)
        if not data:
            return jsonify(ResponseContract(False, "Client not found.").to_dict()), 404
        client = data[0]
        transactions = CreditTransaction.get_by_client(client_id)
        return jsonify(ResponseContract(True, "OK", {
            "credits": float(client.get("credits", 0)),
            "transactions": transactions,
        }).to_dict()), 200
    except Exception as e:
        return error_response(e)


@client_bp.route("/<client_id>/invoices", methods=["GET"])
@require_auth
def list_client_invoices(client_id):
    try:
        data = invoice_svc.get_invoices_by_client(client_id)
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return error_response(e)


@client_bp.route("/<client_id>/payments", methods=["GET"])
@require_auth
def list_client_payments(client_id):
    try:
        data = payment_svc.get_payments_by_client(client_id)
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return error_response(e)


@client_bp.route("/<client_id>/students", methods=["GET"])
@require_auth
def list_client_students(client_id):
    try:
        data = svc.get_client_students(client_id)
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return error_response(e)


@client_bp.route("", methods=["POST"])
@require_auth
def create_client():
    try:
        body = request.get_json()
        validate(body, "client")
        result = svc.create_client(body)
        audit.log(g.user.id, "CREATE", "client",
                  result[0].get("client_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "Client created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@client_bp.route("/<client_id>", methods=["PUT"])
@require_auth
def update_client(client_id):
    try:
        body = request.get_json()
        validate(body, "client", partial=True)
        result = svc.update_client(client_id, body)
        audit.log(g.user.id, "UPDATE", "client", client_id, None, body)
        return jsonify(ResponseContract(True, "Client updated.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@client_bp.route("/<client_id>", methods=["DELETE"])
@require_auth
def delete_client(client_id):
    try:
        svc.delete_client(client_id)
        audit.log(g.user.id, "DELETE", "client", client_id)
        return jsonify(ResponseContract(True, "Client deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
