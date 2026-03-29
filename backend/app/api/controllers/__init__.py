from backend.app.api.controllers.attendance_policy import attendance_policy_bp
from backend.app.api.controllers.audit import audit_bp
from backend.app.api.controllers.client import client_bp
from backend.app.api.controllers.instructor import instructor_bp
from backend.app.api.controllers.invoice import invoice_bp
from backend.app.api.controllers.lesson import lesson_bp

__all__ = [
    "attendance_policy_bp",
    "audit_bp",
    "client_bp",
    "instructor_bp",
    "invoice_bp",
    "lesson_bp",
]
