from dataclasses import dataclass

from backend.app.domain.value_objects.people.contact_info import ContactInfo
from backend.app.domain.value_objects.people.person_name import PersonName


@dataclass
class PersonEntity:
    """A uniquely identifiable person record."""
    person_id: str
    name: PersonName
    contact: ContactInfo

    @classmethod
    def from_dict(cls, d: dict) -> "PersonEntity":
        return cls(
            person_id=d["person_id"],
            name=PersonName(d["name"]),
            contact=ContactInfo(
                email=d.get("email"),
                phone=d.get("phone"),
            ),
        )

    def to_dict(self) -> dict:
        return {
            "person_id": self.person_id,
            "name": self.name.value,
            "email": self.contact.email,
            "phone": self.contact.phone,
        }
