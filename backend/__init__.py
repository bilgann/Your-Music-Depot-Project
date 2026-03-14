from flask import Flask

from backend.app.controllers.user import user_bp
from backend.app.logging.database_logger import DBLogger
from backend.app.singletons.auth import Auth
from backend.app.singletons.database import DatabaseConnection


def build_app():
    app = Flask(__name__)

    logger = DBLogger("app_logger").get_logger()
    DatabaseConnection(logger=logger)
    Auth(logger=logger)

    app.register_blueprint(user_bp)

    return app