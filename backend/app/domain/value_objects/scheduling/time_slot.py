from dataclasses import dataclass


@dataclass(frozen=True)
class TimeSlot:
    """A bounded time window with an ISO-format start and end."""
    start_time: str
    end_time: str

    @classmethod
    def from_dict(cls, d: dict) -> "TimeSlot":
        return cls(start_time=d["start_time"], end_time=d["end_time"])

    def to_dict(self) -> dict:
        return {"start_time": self.start_time, "end_time": self.end_time}
