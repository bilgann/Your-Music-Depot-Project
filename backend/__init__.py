from flask import Flask

from backend.app.controllers.instructor import instructor_bp
from backend.app.controllers.invoice import invoice_bp
from backend.app.controllers.lesson import lesson_bp
from backend.app.controllers.payment import payment_bp
from backend.app.controllers.room import room_bp
from backend.app.controllers.student import student_bp
from backend.app.controllers.user import user_bp
from backend.app.logging.database import DBLogger
from backend.app.singletons.auth import Auth
from backend.app.singletons.database import DatabaseConnection


def build_app():
    app = Flask(__name__)

    logger = DBLogger("db_logger").get_logger()
    DatabaseConnection(logger=logger)
    Auth(logger=logger)

    app.register_blueprint(user_bp)
    app.register_blueprint(instructor_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(invoice_bp)
    app.register_blueprint(payment_bp)

    return app