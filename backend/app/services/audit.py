"""
Audit logging service — records who changed what and when.

All writes are best-effort: a failure here must never break the primary
operation that triggered it. Callers should not catch exceptions from log().
"""
from typing import Any

from backend.app.models.audit import AuditLog


def log(
    user_id: str,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    old_value: Any = None,
    new_value: Any = None,
) -> None:
    """
    Persist an audit entry to the audit_log table.

    Parameters
    ----------
    user_id     : ID of the user who performed the action (from g.user.id)
    action      : "CREATE", "UPDATE", or "DELETE"
    entity_type : table name / domain object (e.g. "lesson", "invoice")
    entity_id   : primary key of the affected record (as a string)
    old_value   : dict of field values before the change (UPDATE / DELETE)
    new_value   : dict of field values after the change  (CREATE / UPDATE)
    """
    try:
        AuditLog.create({
            "user_id": str(user_id),
            "action": action.upper(),
            "entity_type": entity_type,
            "entity_id": str(entity_id) if entity_id is not None else None,
            "old_value": old_value,
            "new_value": new_value,
        })
    except Exception:
        pass  # audit failures are silent — they must not interrupt the user's request
