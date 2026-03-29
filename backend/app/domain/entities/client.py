from dataclasses import dataclass, field

from backend.app.domain.value_objects.financial.money import Money
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime


@dataclass
class ClientEntity:
    """A client who may sponsor one or more students.

    blocked_times covers periods when the client's students will be absent
    (e.g. family vacations, holidays observed by the household).
    """
    client_id: str
    person_id: str
    credits: Money = field(default_factory=Money.zero)
    blocked_times: list[BlockedTime] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "ClientEntity":
        return cls(
            client_id=d["client_id"],
            person_id=d["person_id"],
            credits=Money.of(d.get("credits") or 0),
            blocked_times=[
                BlockedTime.from_dict(b) for b in d.get("blocked_times", [])
            ],
        )

    def to_dict(self) -> dict:
        return {
            "client_id": self.client_id,
            "person_id": self.person_id,
            "credits": self.credits.amount,
            "blocked_times": [b.to_dict() for b in self.blocked_times],
        }
