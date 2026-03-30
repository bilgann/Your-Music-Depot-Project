from flask import jsonify

from backend.app.common.errors import DomainError
from backend.app.domain.exceptions.exceptions import ConflictError, NotFoundError, ValidationError
from backend.app.infrastructure.database.errors import parse_db_error
from backend.app.api.contracts.response import ResponseContract

# ── Per-resource schemas ──────────────────────────────────────────────────────
# "required": fields that must be present and non-empty on POST.
# "types":    optional type checks applied whenever the field is present.

_SCHEMAS: dict = {
    "person": {
        "required": ["name"],
        "types": {"name": str, "email": str, "phone": str},
    },
    "client": {
        "required": [],
        "types": {"name": str, "email": str, "phone": str, "person_id": str},
    },
    "instructor": {
        "required": ["person_id"],
        "types": {"person_id": str, "hourly_rate": (int, float)},
    },
    "student": {
        "required": [],
        "types": {
            "name": str, "email": str, "phone": str,
            "person_id": str, "client_id": str, "age": int,
        },
    },
    "room": {
        "required": ["name"],
        "types": {"name": str, "capacity": int},
    },
    "lesson": {
        "required": ["instructor_id", "room_id", "start_time", "end_time"],
        "types": {
            "start_time": str, "end_time": str,
            "rate": (int, float), "recurrence": str,
            "course_id": str,
        },
    },
    "lesson_enrollment": {
        "required": ["student_id"],
        "types": {"student_id": str},
    },
    "invoice": {
        "required": ["student_id"],
        "types": {"amount_paid": (int, float)},
    },
    "invoice_item": {
        "required": ["description", "amount"],
        "types": {
            "item_type": str, "description": str,
            "amount": (int, float), "occurrence_id": str,
        },
    },
    "payment": {
        "required": ["invoice_id", "amount"],
        "types": {"amount": (int, float)},
    },
    "course": {
        "required": ["name", "room_id", "recurrence", "start_time", "end_time", "period_start", "period_end"],
        "types": {
            "name": str, "description": str, "room_id": str,
            "recurrence": str, "start_time": str, "end_time": str,
            "period_start": str, "period_end": str,
            "capacity": int, "status": str,
        },
    },
    "course_enrollment": {
        "required": ["student_id"],
        "types": {"student_id": str},
    },
    "course_instructor": {
        "required": ["instructor_id"],
        "types": {"instructor_id": str},
    },
    "credential": {
        "required": ["instructor_id", "credential_type"],
        "types": {
            "instructor_id": str, "credential_type": str,
            "issued_by": str, "issued_date": str,
            "valid_from": str, "valid_until": str,
        },
    },
    "compatibility": {
        "required": ["instructor_id", "student_id", "verdict", "initiated_by"],
        "types": {
            "instructor_id": str, "student_id": str,
            "verdict": str, "reason": str, "initiated_by": str,
        },
    },
}


# ── Validation ────────────────────────────────────────────────────────────────

def validate(data, resource: str, partial: bool = False) -> None:
    """
    Validate a request body against the named resource schema.
    - partial=False (POST): all required fields must be present and non-empty.
    - partial=True  (PUT):  skip required-field check; only type-check fields
                            that are actually present in the payload.
    Raises ValidationError with a list of field-level dicts on failure.
    """
    if data is None:
        raise ValidationError([{"field": "_body", "message": "Request body must be JSON."}])

    schema = _SCHEMAS.get(resource, {})
    errors = []

    if not partial:
        for field in schema.get("required", []):
            value = data.get(field)
            if value is None or value == "":
                errors.append({"field": field, "message": f"{field} is required."})

    for field, expected in schema.get("types", {}).items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected):
                type_label = (
                    expected.__name__
                    if not isinstance(expected, tuple)
                    else " or ".join(t.__name__ for t in expected)
                )
                errors.append({"field": field, "message": f"{field} must be {type_label}."})

    if errors:
        raise ValidationError(errors)


# ── Unified error → response ──────────────────────────────────────────────────

def error_response(exc: Exception):
    """
    Convert any exception to a standardised (flask.Response, status_code) tuple.

    Only DomainError subclasses expose their message to the client. All other
    exceptions (ApplicationError, InfrastructureError, raw DB errors, etc.)
    are mapped via parse_db_error first; if they still aren't DomainErrors they
    return a generic 500 so internal details are never leaked.
    """
    if isinstance(exc, ValidationError):
        body = ResponseContract(False, str(exc), errors=exc.errors).to_dict()
        return jsonify(body), 422

    if isinstance(exc, NotFoundError):
        body = ResponseContract(False, str(exc)).to_dict()
        return jsonify(body), 404

    if isinstance(exc, ConflictError):
        body = ResponseContract(False, str(exc)).to_dict()
        return jsonify(body), 409

    if isinstance(exc, DomainError):
        body = ResponseContract(False, str(exc)).to_dict()
        return jsonify(body), 400

    # Attempt to map raw DB/infrastructure errors to a DomainError
    mapped = parse_db_error(exc)
    if mapped is not exc:
        return error_response(mapped)

    # Non-domain errors never expose internal details
    body = ResponseContract(False, "An unexpected error occurred.").to_dict()
    return jsonify(body), 500
