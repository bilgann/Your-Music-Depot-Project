from flask import Blueprint, request, jsonify

from backend.app.contracts.response import ResponseContract
from backend.app.singletons.auth import Auth

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/login', methods=['POST'])
def login():
    username = request.args.get("username")
    password = request.args.get("password")

    token = Auth().authenticate(username, password)

    if token:
        return jsonify(ResponseContract(True, f"{username} logged in successfully.", token).to_dict()), 200
    return jsonify(ResponseContract(False, f"Login failed for {username}.").to_dict()), 401


@user_bp.route("/logout", methods=["DELETE"])
def logout():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify(ResponseContract(False, "No token provided.").to_dict()), 401

    token = auth_header.split(" ", 1)[1]
    Auth().drop_token(token)
    return jsonify(ResponseContract(True, "Logged out successfully.").to_dict()), 200