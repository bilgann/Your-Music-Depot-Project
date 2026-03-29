from dataclasses import dataclass, field
from typing import Optional

from backend.app.domain.value_objects.lesson.room_instrument import RoomInstrument
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime


@dataclass
class RoomEntity:
    """A physical room where lessons are held.

    blocked_times covers periods when the room is unavailable
    (e.g. building closures, maintenance, holidays).
    """
    room_id: str
    name: str
    capacity: Optional[int] = None
    instruments: list[RoomInstrument] = field(default_factory=list)
    blocked_times: list[BlockedTime] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "RoomEntity":
        return cls(
            room_id=d["room_id"],
            name=d["name"],
            capacity=d.get("capacity"),
            instruments=[
                RoomInstrument.from_dict(i)
                for i in d.get("instruments", [])
            ],
            blocked_times=[
                BlockedTime.from_dict(b) for b in d.get("blocked_times", [])
            ],
        )

    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id,
            "name": self.name,
            "capacity": self.capacity,
            "instruments": [i.to_dict() for i in self.instruments],
            "blocked_times": [b.to_dict() for b in self.blocked_times],
        }
