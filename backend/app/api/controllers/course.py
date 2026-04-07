from flask import Blueprint, g, request, jsonify

from backend.app.api.middleware.auth import require_admin, require_auth
from backend.app.api.contracts.response import ResponseContract
from backend.app.api.contracts.validation import error_response, validate
import backend.app.application.services.course as svc
import backend.app.application.services.audit as audit

course_bp = Blueprint("courses", __name__, url_prefix="/api/courses")


@course_bp.route("", methods=["GET"])
@require_auth
def list_courses():
    try:
        instructor_id = request.args.get("instructor_id")
        student_id    = request.args.get("student_id")
        if instructor_id:
            data = svc.get_courses_by_instructor(instructor_id)
        elif student_id:
            data = svc.get_courses_by_student(student_id)
        else:
            data = svc.get_all_courses()
        return jsonify(ResponseContract(True, "OK", data).to_dict()), 200
    except Exception as e:
        return error_response(e)


@course_bp.route("/<course_id>", methods=["GET"])
@require_auth
def get_course(course_id):
    try:
        data = svc.get_course_by_id(course_id)
        if not data:
            return jsonify(ResponseContract(False, "Course not found.").to_dict()), 404
        return jsonify(ResponseContract(True, "OK", data[0]).to_dict()), 200
    except Exception as e:
        return error_response(e)


@course_bp.route("", methods=["POST"])
@require_admin
def create_course():
    try:
        body = request.get_json()
        validate(body, "course")
        result = svc.create_course(body)
        audit.log(g.user.user_id, "CREATE", "course",
                  result[0].get("course_id") if result else None, None, body)
        return jsonify(ResponseContract(True, "Course created.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@course_bp.route("/<course_id>", methods=["PUT"])
@require_admin
def update_course(course_id):
    try:
        body = request.get_json()
        validate(body, "course", partial=True)
        result = svc.update_course(course_id, body)
        audit.log(g.user.user_id, "UPDATE", "course", course_id, None, body)
        return jsonify(ResponseContract(True, "Course updated.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@course_bp.route("/<course_id>", methods=["DELETE"])
@require_admin
def delete_course(course_id):
    try:
        svc.delete_course(course_id)
        audit.log(g.user.user_id, "DELETE", "course", course_id)
        return jsonify(ResponseContract(True, "Course deleted.").to_dict()), 200
    except Exception as e:
        return error_response(e)


# ── Roster ────────────────────────────────────────────────────────────────────

@course_bp.route("/<course_id>/students", methods=["POST"])
@require_admin
def enroll_student(course_id):
    try:
        body = request.get_json()
        validate(body, "course_enrollment")
        result = svc.enroll_student(course_id, body["student_id"])
        audit.log(g.user.user_id, "CREATE", "course_enrollment", course_id, None,
                  {"student_id": body["student_id"]})
        return jsonify(ResponseContract(True, "Student enrolled in course.", result).to_dict()), 201
    except Exception as e:
        return error_response(e)


@course_bp.route("/<course_id>/students/<student_id>", methods=["DELETE"])
@require_admin
def unenroll_student(course_id, student_id):
    try:
        result = svc.unenroll_student(course_id, student_id)
        audit.log(g.user.user_id, "DELETE", "course_enrollment", course_id, None,
                  {"student_id": student_id})
        return jsonify(ResponseContract(True, "Student unenrolled from course.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@course_bp.route("/<course_id>/instructors", methods=["POST"])
@require_admin
def add_instructor(course_id):
    try:
        body = request.get_json()
        validate(body, "course_instructor")
        result = svc.add_instructor(course_id, body["instructor_id"])
        audit.log(g.user.user_id, "UPDATE", "course", course_id, None,
                  {"added_instructor": body["instructor_id"]})
        return jsonify(ResponseContract(True, "Instructor added to course.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


@course_bp.route("/<course_id>/instructors/<instructor_id>", methods=["DELETE"])
@require_admin
def remove_instructor(course_id, instructor_id):
    try:
        result = svc.remove_instructor(course_id, instructor_id)
        audit.log(g.user.user_id, "UPDATE", "course", course_id, None,
                  {"removed_instructor": instructor_id})
        return jsonify(ResponseContract(True, "Instructor removed from course.", result).to_dict()), 200
    except Exception as e:
        return error_response(e)


# ── Schedule projection ───────────────────────────────────────────────────────

@course_bp.route("/<course_id>/project", methods=["POST"])
@require_admin
def project_schedule(course_id):
    """
    POST /api/courses/<course_id>/project
    Expands the course recurrence into LessonOccurrence records.
    Idempotent — deletes and re-projects each time.
    """
    try:
        result = svc.project_course_schedule(course_id)
        audit.log(g.user.user_id, "CREATE", "lesson_occurrence", course_id, None,
                  {"projected": len(result)})
        return jsonify(ResponseContract(
            True, f"Projected {len(result)} occurrence(s).", result
        ).to_dict()), 201
    except Exception as e:
        return error_response(e)
