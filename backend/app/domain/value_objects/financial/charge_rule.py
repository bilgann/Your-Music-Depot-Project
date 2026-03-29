from dataclasses import dataclass


@dataclass(frozen=True)
class ChargeRule:
    """Fun with finance charge rules.

    charge_type: "none" | "flat" | "percentage"
    charge_value: flat dollar amount or percentage; negative values apply
                  discounts or tax credits (e.g. -10 for a 10% discount).

    Examples:
        ChargeRule("flat", 25)          # charge CAD 25 flat for a late cancel
        ChargeRule("percentage", 50)    # charge 50% of the lesson rate for an absence
        ChargeRule("percentage", -10)   # apply a 10% di scount (e.g. sibling rate)
        ChargeRule("flat", -5)          # apply a CAD 5 credit for a makeup lesson
        ChargeRule.none()               # no charge / no adjustment
    """
    charge_type: str
    charge_value: float

    @classmethod
    def none(cls) -> "ChargeRule":
        return cls(charge_type="none", charge_value=0)

    def to_dict(self) -> dict:
        return {"charge_type": self.charge_type, "charge_value": self.charge_value}
