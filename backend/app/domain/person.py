"""
Person-linked entity creation domain rules.

Encapsulates the two-mode creation pattern used by both Client and Student:

  Mode A — new person:  caller provides name (+ optional email / phone).
                        A Person row is created and its person_id is injected.
  Mode B — link existing: caller provides person_id directly.
                        Person fields are stripped from the entity payload.

No database access.  The caller is responsible for creating the Person row
when Mode A is selected (i.e. when prepare_person_linked_create returns a
non-None person_fields dict).
"""

from backend.app.exceptions.base import ValidationError

_PERSON_FIELDS = ("name", "email", "phone")


def prepare_person_linked_create(data: dict) -> tuple[dict | None, dict]:
    """
    Validate and split a creation payload into person fields and entity fields.

    Returns:
        (person_fields, entity_data)

        If person_id is absent (Mode A):
            - Validates that name is present.
            - Pops name/email/phone out of entity_data and returns them as
              person_fields (caller must create the Person row).

        If person_id is present (Mode B):
            - Strips any name/email/phone from entity_data (they are ignored).
            - Returns None as person_fields.

    Raises:
        ValidationError: if Mode A is used but name is missing.
    """
    data = dict(data)

    if not data.get("person_id"):
        if not data.get("name"):
            raise ValidationError([{
                "field": "name",
                "message": "name is required when person_id is not provided.",
            }])
        person_fields = {k: data.pop(k) for k in _PERSON_FIELDS if k in data}
        return person_fields, data

    # Mode B — person_id supplied; discard any stray person fields
    for k in _PERSON_FIELDS:
        data.pop(k, None)
    return None, data


def extract_person_update_fields(data: dict) -> tuple[dict, dict]:
    """
    Split an update payload into (person_fields, entity_fields).

    Used for update operations where name/email/phone should be written
    to the Person row while other fields go to the entity row.
    """
    data = dict(data)
    person_fields = {k: data.pop(k) for k in _PERSON_FIELDS if k in data}
    return person_fields, data
