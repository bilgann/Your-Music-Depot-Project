from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class AuditLogEntity:
    """An immutable record of a create, update, or delete event."""
    log_id: str
    user_id: str
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None

    @classmethod
    def from_dict(cls, d: dict) -> "AuditLogEntity":
        return cls(
            log_id=d.get("id") or d.get("log_id", ""),
            user_id=d["user_id"],
            action=d["action"],
            entity_type=d["entity_type"],
            entity_id=d.get("entity_id"),
            old_value=d.get("old_value"),
            new_value=d.get("new_value"),
        )

    def to_dict(self) -> dict:
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }
