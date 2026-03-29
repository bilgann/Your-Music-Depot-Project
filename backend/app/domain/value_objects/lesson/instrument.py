from dataclasses import dataclass

from backend.app.domain.exceptions.exceptions import ValidationError

_FAMILIES: frozenset[str] = frozenset({
    "keyboard",
    "strings",
    "woodwind",
    "brass",
    "percussion",
    "voice",
    "other",
})


@dataclass(frozen=True)
class Instrument:
    """A musical instrument or discipline that can be taught.

    family: broad instrument family used for grouping and filtering.

    Examples:
        Instrument("Piano",   "keyboard")
        Instrument("Violin",  "strings")
        Instrument("Trumpet", "brass")
        Instrument("Flute",   "woodwind")
        Instrument("Drums",   "percussion")
        Instrument("Voice",   "voice")
    """

    name: str
    family: str

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValidationError([{
                "field": "instrument",
                "message": "Instrument name must not be blank.",
            }])
        if self.family not in _FAMILIES:
            raise ValidationError([{
                "field": "instrument_family",
                "message": (
                    f"Invalid instrument family '{self.family}'. "
                    f"Must be one of: {', '.join(sorted(_FAMILIES))}."
                ),
            }])

    @property
    def requires_quantity(self) -> bool:
        """Voice is performed, not placed in a room — no quantity applies."""
        return self.family != "voice"

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        return {"name": self.name, "family": self.family}

    @classmethod
    def from_dict(cls, d: dict) -> "Instrument":
        return cls(name=d["name"], family=d["family"])
