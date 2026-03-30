from flask import Blueprint, g, request, jsonify

from backend.app.api.contracts.response import ResponseContract
from backend.app.api.middleware.auth import require_admin
from backend.app.application.singletons.auth import Auth
from backend.app.infrastructure.database.repositories import User

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
    if Auth().get_user(token) is None:
        return jsonify(ResponseContract(False, "Token is invalid or already logged out.").to_dict()), 401
    Auth().drop_token(token)
    return jsonify(ResponseContract(True, "Logged out successfully.").to_dict()), 200


@user_bp.route("/password", methods=["PUT"])
@require_admin
def change_password():
    body = request.get_json()
    current_password = body.get("current_password", "")
    new_password = body.get("new_password", "")
    if not current_password or not new_password:
        return jsonify(ResponseContract(False, "Current and new password are required.").to_dict()), 400
    if len(new_password) < 6:
        return jsonify(ResponseContract(False, "New password must be at least 6 characters.").to_dict()), 400
    success = User.change_password(g.user.user_id, current_password, new_password)
    if not success:
        return jsonify(ResponseContract(False, "Current password is incorrect.").to_dict()), 401
    return jsonify(ResponseContract(True, "Password changed successfully.").to_dict()), 200