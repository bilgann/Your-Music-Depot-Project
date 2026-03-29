"""
Flask decorators that enforce authentication and role-based access control.

Usage:
    @require_auth          — any logged-in user
    @require_admin         — admin role only (instructors get 403)

After a successful check, the authenticated User object is available as
flask.g.user inside the decorated route function.
"""
from functools import wraps

from flask import g, jsonify, request

from backend.app.api.contracts.response import ResponseContract
from backend.app.application.singletons.auth import Auth


def _extract_token() -> str | None:
    """Return the Bearer token from the Authorization header, or None."""
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header.split(" ", 1)[1]
    return None


def require_auth(f):
    """
    Decorator: reject requests that carry no valid JWT.
    Sets g.user to the authenticated User on success.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            body = ResponseContract(False, "Authentication required.").to_dict()
            return jsonify(body), 401
        user = Auth().get_user(token)
        if user is None:
            body = ResponseContract(False, "Invalid or expired session. Please log in again.").to_dict()
            return jsonify(body), 401
        g.user = user
        g.token = token
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """
    Decorator: reject requests from non-admin users.
    Performs full JWT validation (no need to stack @require_auth separately).
    Sets g.user on success.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            body = ResponseContract(False, "Authentication required.").to_dict()
            return jsonify(body), 401
        user = Auth().get_user(token)
        if user is None:
            body = ResponseContract(False, "Invalid or expired session. Please log in again.").to_dict()
            return jsonify(body), 401
        if user.role != "admin":
            body = ResponseContract(False, "Admin access required.").to_dict()
            return jsonify(body), 403
        g.user = user
        g.token = token
        return f(*args, **kwargs)
    return decorated
