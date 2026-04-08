from backend.app.domain.entities.school_schedule import SchoolScheduleEntity
from backend.app.domain.exceptions.exceptions import ConflictError, NotFoundError
from backend.app.domain.value_objects.scheduling.blocked_time import BlockedTime
from backend.app.infrastructure.database.repositories.school_schedule import SchoolSchedule
from backend.app.infrastructure.database.repositories.school_schedule_override import SchoolScheduleOverride


# ── CRUD ─────────────────────────────────────────────────────────────────────

def list_school_schedules(page: int = 1, page_size: int = 20, active_only: bool = False):
    return SchoolSchedule.list(page, page_size, active_only)


def get_school_schedule_by_id(schedule_id: str):
    return SchoolSchedule.get(schedule_id)


def create_school_schedule(data: dict):
    return SchoolSchedule.create(data)


def update_school_schedule(schedule_id: str, data: dict):
    if not SchoolSchedule.get(schedule_id):
        raise NotFoundError("School schedule entry not found.")
    return SchoolSchedule.update(schedule_id, data)


def delete_school_schedule(schedule_id: str):
    if not SchoolSchedule.get(schedule_id):
        raise NotFoundError("School schedule entry not found.")
    return SchoolSchedule.delete(schedule_id)


# ── Overrides ────────────────────────────────────────────────────────────────

def list_overrides(schedule_id: str):
    if not SchoolSchedule.get(schedule_id):
        raise NotFoundError("School schedule entry not found.")
    return SchoolScheduleOverride.get_by_schedule(schedule_id)


def create_override(schedule_id: str, data: dict):
    if not SchoolSchedule.get(schedule_id):
        raise NotFoundError("School schedule entry not found.")
    existing = SchoolScheduleOverride.find(
        schedule_id, data["entity_type"], data["entity_id"],
    )
    if existing:
        raise ConflictError("Override already exists for this entity.")
    data["schedule_id"] = schedule_id
    return SchoolScheduleOverride.create(data)


def delete_override(schedule_id: str, override_id: str):
    rows = SchoolScheduleOverride.get(override_id)
    if not rows or rows[0]["schedule_id"] != schedule_id:
        raise NotFoundError("Override not found.")
    return SchoolScheduleOverride.delete(override_id)


# ── Projection helper ────────────────────────────────────────────────────────

def collect_school_blocked_times(
    entity_checks: list[tuple[str, str]],
) -> list[BlockedTime]:
    """Return BlockedTime objects for active school schedule entries that
    are NOT overridden by any of the given entities.

    Args:
        entity_checks: list of (entity_type, entity_id) pairs to check.
            Example: [("lesson", lesson_id), ("instructor", instr_id), ("room", room_id)]

    Returns:
        List of BlockedTime objects to merge into the projection's blocked list.
    """
    entries = SchoolSchedule.get_active()
    if not entries:
        return []

    schedule_ids = [e["schedule_id"] for e in entries]
    overrides = SchoolScheduleOverride.get_for_schedules(schedule_ids)

    # Fast lookup set: (schedule_id, entity_type, entity_id)
    override_set = {
        (o["schedule_id"], o["entity_type"], o["entity_id"])
        for o in overrides
    }

    blocked: list[BlockedTime] = []
    for entry in entries:
        sid = entry["schedule_id"]
        overridden = any(
            (sid, etype, eid) in override_set
            for etype, eid in entity_checks
        )
        if not overridden:
            entity = SchoolScheduleEntity.from_dict(entry)
            blocked.append(entity.to_blocked_time())

    return blocked
