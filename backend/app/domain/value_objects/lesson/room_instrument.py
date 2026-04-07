from dataclasses import dataclass
from typing import Optional

from backend.app.domain.exceptions.exceptions import ValidationError
from backend.app.domain.value_objects.lesson.instrument import Instrument


@dataclass(frozen=True)
class RoomInstrument:
    """An instrument present in a room, with an optional quantity.

    Voice and other non-physical disciplines have quantity=None.

    Examples:
        RoomInstrument(Instrument("Piano",  "keyboard"), quantity=2)
        RoomInstrument(Instrument("Drums",  "percussion"), quantity=1)
        RoomInstrument(Instrument("Voice",  "voice"), quantity=None)
    """

    instrument: Instrument
    quantity: Optional[int] = None

    def __post_init__(self):
        if self.instrument.requires_quantity:
            if self.quantity is None or self.quantity < 1:
                raise ValidationError([{
                    "field": "quantity",
                    "message": (
                        f"'{self.instrument.name}' requires a quantity of at least 1."
                    ),
                }])
        else:
            if self.quantity is not None:
                raise ValidationError([{
                    "field": "quantity",
                    "message": (
                        f"'{self.instrument.name}' ({self.instrument.family}) "
                        "does not use a quantity."
                    ),
                }])

    def to_dict(self) -> dict:
        return {
            "name": self.instrument.name,
            "family": self.instrument.family,
            "quantity": self.quantity,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RoomInstrument":
        return cls(
            instrument=Instrument(name=d["name"], family=d["family"]),
            quantity=d.get("quantity"),
        )
