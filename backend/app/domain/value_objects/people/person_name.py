from dataclasses import dataclass

from backend.app.domain.exceptions.exceptions import ValidationError


@dataclass(frozen=True)
class PersonName:
    """A non-empty person name."""
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValidationError([{"field": "name", "message": "name must not be blank."}])

    def __str__(self) -> str:
        return self.value
