from flask import Blueprint, g, request, jsonify

from backend.app.contracts.auth_middleware import require_admin
from backend.app.contracts.response import ResponseContract
from backend.app.contracts.validation import error_response, validate
import backend.app.services.payment as svc
import backend.app.services.audit as audit

payment_bp = Blueprint("payments", __name__, url_prefix="/api/payments")


@payment_bp.route("", methods=["GET"])
@require_admin
def list_payments():
    try:
        return jsonify(ResponseContract(True, "OK", svc.get_all_payments()).to_dict()), 200
    except Exception as e:
        return error_response(e)


@payment_bp.route("/<payment_id>", methods=["GET"])
@require_admin
def get_payment(payment_id):
    try:
        data = svc.get_payment_by_id(payment_id)
        if not data:
            return jsonify(ResponseContract(False, "Payment not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@payment_bp.route("", methods=["POST"])
@require_admin
def record_payment():
    """POST /api/payments  —  body: { invoice_id, amount, payment_method?, paid_on?, notes? }"""
    try:
        body = request.get_json()
        validate(body, "payment")
        data = svc.record_payment(body)
        audit.log(g.user.id, "CREATE", "payment",
                  data.get("payment_id"), None, body)
        return jsonify(ResponseContract(True, "Payment recorded.", data).to_dict()), 201
    except Exception as e:
        return error_response(e)


@payment_bp.route("/<payment_id>", methods=["DELETE"])
@require_admin
def delete_payment(payment_id):
    try:
        svc.delete_payment(payment_id)
        audit.log(g.user.id, "DELETE", "payment", payment_id)
        return jsonify(ResponseContract(True, "Payment deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)
