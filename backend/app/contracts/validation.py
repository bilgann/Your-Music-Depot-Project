from flask import jsonify

from backend.app.exceptions.base import ConflictError, NotFoundError, ValidationError
from backend.app.contracts.response import ResponseContract

# ── Per-resource schemas ──────────────────────────────────────────────────────
# "required": fields that must be present and non-empty on POST.
# "types":    optional type checks applied whenever the field is present.

_SCHEMAS: dict = {
    "instructor": {
        "required": ["name"],
        "types": {"name": str, "email": str, "phone": str},
    },
    "student": {
        "required": ["name"],
        "types": {"name": str, "email": str, "phone": str},
    },
    "room": {
        "required": ["name"],
        "types": {"name": str, "capacity": int},
    },
    "lesson": {
        "required": ["student_id", "instructor_id", "room_id", "start_time", "end_time"],
        "types": {"start_time": str, "end_time": str, "rate": (int, float)},
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

# ── PostgreSQL error codes returned by Supabase ───────────────────────────────
_PG_FK_VIOLATION = "23503"
_PG_UNIQUE_VIOLATION = "23505"
_PG_NOT_NULL_VIOLATION = "23502"


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


# ── DB-error mapping ──────────────────────────────────────────────────────────

def parse_db_error(exc: Exception) -> Exception:
    """
    Inspect a raw Supabase / PostgreSQL exception and return a typed
    application exception, or the original if the cause is unknown.
    """
    msg = str(exc).lower()

    if _PG_FK_VIOLATION in msg or "foreign key" in msg:
        return ConflictError(
            "Cannot complete this operation: a related record still exists or is required."
        )
    if _PG_UNIQUE_VIOLATION in msg or "unique" in msg or "duplicate" in msg:
        return ConflictError("A record with these values already exists.")
    if _PG_NOT_NULL_VIOLATION in msg or "not-null" in msg or "not null" in msg:
        return ValidationError(
            [{"field": "_body", "message": "A required database field is missing."}]
        )
    return exc


# ── Unified error → response ──────────────────────────────────────────────────

def error_response(exc: Exception):
    """
    Convert any exception to a standardized (flask.Response, status_code) tuple.
    Never exposes raw stack traces or internal error details to the client.
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

    # Try mapping raw DB errors before falling back to generic 500
    mapped = parse_db_error(exc)
    if mapped is not exc:
        return error_response(mapped)

    body = ResponseContract(False, "An unexpected error occurred.").to_dict()
    return jsonify(body), 500
