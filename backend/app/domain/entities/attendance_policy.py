from dataclasses import dataclass, field
from backend.app.domain.value_objects import ChargeRule


@dataclass
class AttendancePolicyEntity:
    """Defines how absences, cancellations, and late cancellations are charged."""
    policy_id: str
    name: str
    absent: ChargeRule = field(default_factory=ChargeRule.none)
    cancel: ChargeRule = field(default_factory=ChargeRule.none)
    late_cancel: ChargeRule = field(default_factory=ChargeRule.none)
    is_default: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "AttendancePolicyEntity":
        return cls(
            policy_id=d["policy_id"],
            name=d["name"],
            absent=ChargeRule(
                charge_type=d.get("absent_charge_type", "none"),
                charge_value=float(d.get("absent_charge_value") or 0),
            ),
            cancel=ChargeRule(
                charge_type=d.get("cancel_charge_type", "none"),
                charge_value=float(d.get("cancel_charge_value") or 0),
            ),
            late_cancel=ChargeRule(
                charge_type=d.get("late_cancel_charge_type", "none"),
                charge_value=float(d.get("late_cancel_charge_value") or 0),
            ),
            is_default=bool(d.get("is_default", False)),
        )

    def to_dict(self) -> dict:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "absent_charge_type": self.absent.charge_type,
            "absent_charge_value": self.absent.charge_value,
            "cancel_charge_type": self.cancel.charge_type,
            "cancel_charge_value": self.cancel.charge_value,
            "late_cancel_charge_type": self.late_cancel.charge_type,
            "late_cancel_charge_value": self.late_cancel.charge_value,
            "is_default": self.is_default,
        }
