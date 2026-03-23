from flask import Blueprint, request, jsonify

from backend.app.contracts.response import ResponseContract
import backend.app.services.payment as svc

payment_bp = Blueprint("payments", __name__, url_prefix="/api/payments")


@payment_bp.route("", methods=["GET"])
def list_payments():
    try:
        data = svc.get_all_payments()
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@payment_bp.route("/<payment_id>", methods=["GET"])
def get_payment(payment_id):
    try:
        data = svc.get_payment_by_id(payment_id)
        if not data:
            return jsonify(ResponseContract(False, "Payment not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@payment_bp.route("", methods=["POST"])
def create_payment():
    try:
        data = svc.create_payment(request.get_json())
        return jsonify(ResponseContract(True, "Payment created.", data).to_dict()), 201
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@payment_bp.route("/<payment_id>", methods=["PUT"])
def update_payment(payment_id):
    try:
        data = svc.update_payment(payment_id, request.get_json())
        return jsonify(ResponseContract(True, "Payment updated.", data).to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500


@payment_bp.route("/<payment_id>", methods=["DELETE"])
def delete_payment(payment_id):
    try:
        svc.delete_payment(payment_id)
        return jsonify(ResponseContract(True, "Payment deleted.").to_dict()), 200
    except Exception as e:
        return jsonify(ResponseContract(False, str(e)).to_dict()), 500