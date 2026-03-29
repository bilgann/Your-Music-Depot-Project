import datetime
from decimal import Decimal

from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS

from backend.app.contracts.response import ResponseContract
from backend.app.controllers.audit import audit_bp
from backend.app.controllers.client import client_bp
from backend.app.controllers.instructor import instructor_bp
from backend.app.controllers.person import person_bp
from backend.app.controllers.invoice import invoice_bp
from backend.app.controllers.lesson import lesson_bp
from backend.app.controllers.payment import payment_bp
from backend.app.controllers.room import room_bp
from backend.app.controllers.student import student_bp
from backend.app.controllers.user import user_bp
from backend.app.logging.database import DBLogger
from backend.app.singletons.auth import Auth
from backend.app.singletons.database import DatabaseConnection


class _JSONProvider(DefaultJSONProvider):
    """Extend Flask's default serializer to handle types Supabase returns."""

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def build_app():
    app = Flask(__name__)

    # Custom JSON serializer — must be applied before any jsonify calls
    app.json = _JSONProvider(app)

    # CORS — allow the Next.js dev server; tighten origins in production
    CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://localhost:3001"]}},
         supports_credentials=True)

    logger = DBLogger("db_logger").get_logger()
    DatabaseConnection(logger=logger)
    Auth(logger=logger)

    app.register_blueprint(user_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(person_bp)
    app.register_blueprint(instructor_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(invoice_bp)
    app.register_blueprint(payment_bp)

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(ResponseContract(False, "Endpoint not found.").to_dict()), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify(ResponseContract(False, "Method not allowed.").to_dict()), 405

    @app.errorhandler(Exception)
    def unhandled_exception(_):
        return jsonify(ResponseContract(False, "An unexpected error occurred.").to_dict()), 500

    return app
