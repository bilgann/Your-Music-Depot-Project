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
        "required": ["name"],
        "types": {"name": str, "email": str, "phone": str},
    },
    "student": {
        "required": [],
        "types": {"name": str, "email": str, "phone": str, "person_id": str, "client_id": str},
    },
    "room": {
        "required": ["name"],
        "types": {"name": str, "capacity": int},
    },
    "lesson": {
        "required": ["instructor_id", "room_id", "start_time", "end_time"],
        "types": {"start_time": str, "end_time": str, "rate": (int, float), "recurrence": str},
    },
    "lesson_enrollment": {
        "required": ["student_id"],
        "types": {"student_id": str},
    },
    "invoice": {
        "required": ["student_id", "total_amount"],
        "types": {"total_amount": (int, float), "amount_paid": (int, float)},
    },
    "payment": {
        "required": ["invoice_id", "amount"],
        "types": {"amount": (int, float)},
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
