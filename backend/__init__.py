from flask import Flask
from app.routes.auth import auth_bp


def build_app():
    app = Flask(__name__)

    # Register API routes
    # app.register_blueprint(lessons_bp)
    app.register_blueprint(auth_bp)

    return app