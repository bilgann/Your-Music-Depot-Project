from flask import Blueprint, g, request, jsonify

from backend.app.api.middleware.auth import require_admin, require_auth
from backend.app.api.contracts.response import ResponseContract
from backend.app.api.contracts.validation import error_response, validate
from backend.app.domain.exceptions.exceptions import ValidationError
import backend.app.application.services.lesson as svc
import backend.app.application.services.audit as audit

lesson_bp = Blueprint("lessons", __name__, url_prefix="/api/lessons")


# ── Lesson template CRUD ──────────────────────────────────────────────────────

@lesson_bp.route("", methods=["GET"])
@require_auth
def list_lessons():
    try:
        week_start = request.args.get("weekStart")
        week_end   = request.args.get("weekEnd")
        data = (
            svc.get_lessons_for_week(week_start, week_end)
            if week_start and week_end
            else svc.get_all_lessons()
        )
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return error_response(e)


@lesson_bp.route("/<lesson_id>", methods=["GET"])
@require_auth
def get_lesson(lesson_id):
    try:
        data = svc.get_lesson_by_id(lesson_id)
        if not data:
            return jsonify(ResponseContract(False, "Lesson not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@lesson_bp.route("", methods=["POST"])
@require_admin
def create_lesson():
    try:
        body = request.get_json()
        validate(body, "lesson")
        result = svc.create_lesson(body)
        audit.log(g.user.user_id, "CREATE", "lesson",
                  result[0].get("lesson_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "Lesson created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@lesson_bp.route("/<lesson_id>", methods=["PUT"])
@require_admin
def update_lesson(lesson_id):
    try:
        body = request.get_json()
        validate(body, "lesson", partial=True)
        result = svc.update_lesson(lesson_id, body)
        audit.log(g.user.user_id, "UPDATE", "lesson", lesson_id, None, body)
        return jsonify(ResponseContract(True, "Lesson updated.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@lesson_bp.route("/<lesson_id>", methods=["DELETE"])
@require_admin
def delete_lesson(lesson_id):
    try:
        svc.delete_lesson(lesson_id)
        audit.log(g.user.user_id, "DELETE", "lesson", lesson_id)
        return jsonify(ResponseContract(True, "Lesson deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)


# ── Schedule projection ───────────────────────────────────────────────────────

@lesson_bp.route("/<lesson_id>/project", methods=["POST"])
@require_admin
def project_schedule(lesson_id):
    """
    POST /api/lessons/<lesson_id>/project
    Expands the lesson recurrence into LessonOccurrence records.
    Idempotent — deletes and re-projects each time.
    """
    try:
        result = svc.project_lesson_schedule(lesson_id)
        audit.log(g.user.user_id, "CREATE", "lesson_occurrence", lesson_id, None,
                  {"projected": len(result)})
        return jsonify(ResponseContract(
            True, f"Projected {len(result)} occurrence(s).", result
        ).to_dict()), 201
    except Exception as e:
        return error_response(e)


# ── Occurrence enrollment ─────────────────────────────────────────────────────

@lesson_bp.route("/occurrences/<occurrence_id>/students", methods=["GET"])
@require_auth
def list_occurrence_students(occurrence_id):
    try:
        data = svc.get_occurrence_students(occurrence_id)
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return error_response(e)


@lesson_bp.route("/occurrences/<occurrence_id>/enroll", methods=["POST"])
@require_admin
def enroll_student(occurrence_id):
    try:
        body = request.get_json()
        validate(body, "lesson_enrollment")
        result = svc.enroll_student_in_occurrence(occurrence_id, body["student_id"])
        audit.log(g.user.user_id, "CREATE", "lesson_enrollment", occurrence_id, None,
                  {"student_id": body["student_id"]})
        return jsonify(ResponseContract(True, "Student enrolled.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@lesson_bp.route("/occurrences/<occurrence_id>/enroll/<student_id>/attendance", methods=["PUT"])
@require_auth
def record_attendance(occurrence_id, student_id):
    """PUT body: { "attendance_status": "Present" | "Absent" | "Cancelled" | "Late Cancel" | "Excused" }"""
    try:
        body   = request.get_json() or {}
        status = body.get("attendance_status")
        valid  = {"Present", "Absent", "Cancelled", "Late Cancel", "Excused"}
        if status not in valid:
            raise ValidationError([{
                "field": "attendance_status",
                "message": f"Must be one of: {', '.join(sorted(valid))}.",
            }])
        result = svc.record_attendance(occurrence_id, student_id, status)
        audit.log(g.user.user_id, "UPDATE", "lesson_enrollment", occurrence_id, None,
                  {"student_id": student_id, "attendance_status": status})
        return jsonify(ResponseContract(True, "Attendance recorded.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@lesson_bp.route("/occurrences/<occurrence_id>/enroll/<student_id>", methods=["DELETE"])
@require_admin
def unenroll_student(occurrence_id, student_id):
    try:
        svc.unenroll_student_from_occurrence(occurrence_id, student_id)
        audit.log(g.user.user_id, "DELETE", "lesson_enrollment", occurrence_id, None,
                  {"student_id": student_id})
        return jsonify(ResponseContract(True, "Student unenrolled.").to_dict()), 200
    except Exception as e:
        return error_response(e)
