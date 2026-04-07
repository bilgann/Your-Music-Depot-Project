"""
PostgreSQL / Supabase error mapping.

Translates raw database exceptions into typed DomainErrors so the layers
above never need to know about vendor-specific error codes.
"""

from backend.app.domain.exceptions.exceptions import ConflictError, ValidationError

# ── PostgreSQL error codes ────────────────────────────────────────────────────

PG_FK_VIOLATION = "23503"
PG_UNIQUE_VIOLATION = "23505"
PG_NOT_NULL_VIOLATION = "23502"
PG_CHECK_VIOLATION = "23514"

# ── Fallback messages ─────────────────────────────────────────────────────────

_MSG_FK = "Cannot complete this operation: a related record still exists or is required."
_MSG_UNIQUE = "A record with these values already exists."
_MSG_NOT_NULL = "A required database field is missing."


def parse_db_error(exc: Exception) -> Exception:
    """
    Inspect a raw Supabase / PostgreSQL exception and return a typed
    DomainError, or the original exception if the cause is unknown.
    """
    msg = str(exc).lower()

    if PG_FK_VIOLATION in msg or "foreign key" in msg:
        return ConflictError(_MSG_FK)
    if PG_UNIQUE_VIOLATION in msg or "unique" in msg or "duplicate" in msg:
        return ConflictError(_MSG_UNIQUE)
    if PG_NOT_NULL_VIOLATION in msg or "not-null" in msg or "not null" in msg:
        return ValidationError([{"field": "_body", "message": _MSG_NOT_NULL}])
    if PG_CHECK_VIOLATION in msg or "check" in msg and "violat" in msg:
        return ValidationError([{"field": "_body", "message": "A value violates a database constraint."}])
    return exc
