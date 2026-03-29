from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from backend.app.domain.value_objects.lesson.instrument import Instrument
from backend.app.domain.value_objects.lesson.instrument_proficiency import InstrumentProficiency
from backend.app.domain.value_objects.lesson.skill_level import SkillLevel
from backend.app.domain.value_objects.scheduling.date_range import DateRange


VALID_CREDENTIAL_TYPES = frozenset({
    "musical",           # instrument / teaching qualification (default)
    "cpr",               # CPR / first aid
    "special_ed",        # special education certification
    "vulnerable_sector", # police check / vulnerable sector screening
    "first_aid",         # general first aid
    "other",
})


@dataclass
class CredentialEntity:
    """A teaching credential held by an instructor.

    credential_type  Categorises the credential so CompatibilityService can match
                     it against a StudentEntity's TeachingRequirement("credential", …).
                     Defaults to "musical" for backward compatibility.
    proficiencies    Instrument / skill-range coverage (relevant for "musical" type).
    validity         Date range during which the credential is active.
    """
    credential_id:   str
    instructor_id:   str
    proficiencies:   list[InstrumentProficiency]
    credential_type: str = "musical"
    validity:        Optional[DateRange] = None
    issued_by:       Optional[str] = None
    issued_date:     Optional[str] = None

    @property
    def is_expired(self) -> bool:
        """True if a validity range is set and today is past the end date."""
        if self.validity is None:
            return False
        return date.today().isoformat() > self.validity.period_end

    def can_teach(self, instrument: Instrument, level: SkillLevel) -> bool:
        """True if any proficiency in this credential covers the instrument and level."""
        return any(p.can_teach(instrument, level) for p in self.proficiencies)

    @classmethod
    def from_dict(cls, d: dict) -> "CredentialEntity":
        valid_start = d.get("valid_from")
        valid_end   = d.get("valid_until")
        return cls(
            credential_id=d["credential_id"],
            instructor_id=d["instructor_id"],
            proficiencies=[
                InstrumentProficiency.from_dict(p)
                for p in d.get("proficiencies", [])
            ],
            credential_type=d.get("credential_type", "musical"),
            validity=(
                DateRange(period_start=valid_start, period_end=valid_end)
                if valid_start and valid_end
                else None
            ),
            issued_by=d.get("issued_by"),
            issued_date=d.get("issued_date"),
        )

    def to_dict(self) -> dict:
        return {
            "credential_id":   self.credential_id,
            "instructor_id":   self.instructor_id,
            "credential_type": self.credential_type,
            "proficiencies":   [p.to_dict() for p in self.proficiencies],
            "valid_from":      self.validity.period_start if self.validity else None,
            "valid_until":     self.validity.period_end if self.validity else None,
            "issued_by":       self.issued_by,
            "issued_date":     self.issued_date,
        }
