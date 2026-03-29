from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ContactInfo:
    """Name and optional contact details for a person or instructor."""
    email: Optional[str] = None
    phone: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "ContactInfo":
        return cls(
            email=d.get("email"),
            phone=d.get("phone"),
        )

    def to_dict(self) -> dict:
        return {"email": self.email, "phone": self.phone}
