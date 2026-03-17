import os
import sys
from typing import Dict, List

# allow: from database import supabase
BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BACKEND_DIR)

from database import supabase  # noqa: E402


def _select_one(table: str, filters: Dict):
    q = supabase.table(table).select("*")
    for k, v in filters.items():
        q = q.eq(k, v)
    res = q.limit(1).execute()
    data = res.data or []
    return data[0] if data else None


def _upsert_by_filter(table: str, lookup: Dict, payload: Dict):
    existing = _select_one(table, lookup)
    if existing:
        q = supabase.table(table).update(payload)
        for k, v in lookup.items():
            q = q.eq(k, v)
        q.execute()
        return _select_one(table, lookup)
    created = supabase.table(table).insert(payload).execute().data
    return created[0] if created else None


def seed_instructors() -> List[Dict]:
    rows = [
        {"full_name": "Avery Cole", "dob": "1988-03-12", "email": "avery.cole@musicdepot.test", "phone": "555-1001"},
        {"full_name": "Noah Reed", "dob": "1985-07-21", "email": "noah.reed@musicdepot.test", "phone": "555-1002"},
        {"full_name": "Mia Hart", "dob": "1990-11-05", "email": "mia.hart@musicdepot.test", "phone": "555-1003"},
        {"full_name": "Liam Brooks", "dob": "1987-01-18", "email": "liam.brooks@musicdepot.test", "phone": "555-1004"},
        {"full_name": "Ella Stone", "dob": "1992-06-30", "email": "ella.stone@musicdepot.test", "phone": "555-1005"},
    ]
    return [_upsert_by_filter("instructor", {"email": r["email"]}, r) for r in rows]


def seed_students() -> List[Dict]:
    rows = []
    for i in range(1, 16):
        rows.append({
            "full_name": f"Student {i:02d}",
            "email": f"student{i:02d}@musicdepot.test",
            "dob": f"200{(i % 10)}-0{((i % 9) + 1)}-1{(i % 9)}",
        })
    return [_upsert_by_filter("student", {"email": r["email"]}, r) for r in rows]


def seed_rooms() -> List[Dict]:
    rows = [
        {"capacity": 2, "instrument_type": "Piano"},
        {"capacity": 2, "instrument_type": "Guitar"},
        {"capacity": 3, "instrument_type": "Violin"},
        {"capacity": 4, "instrument_type": "Drums"},
        {"capacity": 4, "instrument_type": "Voice"},
        {"capacity": 6, "instrument_type": "Piano"},
        {"capacity": 8, "instrument_type": "Guitar"},
    ]
    # no unique constraint shown; use capacity+instrument_type as deterministic lookup
    return [_upsert_by_filter("room", {"capacity": r["capacity"], "instrument_type": r["instrument_type"]}, r) for r in rows]


def seed_instructor_skills(instructors: List[Dict]):
    # table: instructor_skill(instructor_id, instrument, min_skill_level)
    mapping = {
        "avery.cole@musicdepot.test": [("Piano", 2), ("Voice", 3)],
        "noah.reed@musicdepot.test": [("Guitar", 2)],
        "mia.hart@musicdepot.test": [("Violin", 1)],
        "liam.brooks@musicdepot.test": [("Drums", 3)],
        "ella.stone@musicdepot.test": [("Voice", 1), ("Piano", 4)],
    }

    for inst in instructors:
        pairs = mapping.get(inst["email"], [])
        for instrument, min_level in pairs:
            payload = {
                "instructor_id": inst["instructor_id"],
                "instrument": instrument,
                "min_skill_level": min_level,
            }
            _upsert_by_filter(
                "instructor_skill",
                {"instructor_id": inst["instructor_id"], "instrument": instrument},
                payload,
            )


def seed_student_skills(students: List[Dict]):
    # table: student_skill(student_id, instrument, skill_level)
    instruments = ["Piano", "Guitar", "Violin", "Drums", "Voice"]
    for idx, st in enumerate(students):
        inst1 = instruments[idx % len(instruments)]
        inst2 = instruments[(idx + 2) % len(instruments)]

        p1 = {
            "student_id": st["student_id"],
            "instrument": inst1,
            "skill_level": (idx % 5) + 1,  # 1..5
        }
        p2 = {
            "student_id": st["student_id"],
            "instrument": inst2,
            "skill_level": ((idx + 1) % 5) + 1,
        }

        _upsert_by_filter("student_skill", {"student_id": st["student_id"], "instrument": inst1}, p1)
        _upsert_by_filter("student_skill", {"student_id": st["student_id"], "instrument": inst2}, p2)


def seed_lessons(instructors: List[Dict], students: List[Dict], rooms: List[Dict]):
    # 25 lessons (Mon-Fri x 5 slots)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slots = [
        ("09:00:00", "10:00:00"),
        ("10:15:00", "11:15:00"),
        ("13:00:00", "14:00:00"),
        ("14:15:00", "15:15:00"),
        ("16:00:00", "17:00:00"),
    ]
    term = "2026-Spring"
    lesson_types = ["private", "group"]
    instruments = ["Piano", "Guitar", "Violin", "Drums", "Voice"]

    # email -> instructor_id
    instructor_by_email = {i["email"]: i["instructor_id"] for i in instructors}
    instructor_for_instrument = {
        "Piano": instructor_by_email["avery.cole@musicdepot.test"],
        "Guitar": instructor_by_email["noah.reed@musicdepot.test"],
        "Violin": instructor_by_email["mia.hart@musicdepot.test"],
        "Drums": instructor_by_email["liam.brooks@musicdepot.test"],
        "Voice": instructor_by_email["ella.stone@musicdepot.test"],
    }

    # instrument -> room list
    rooms_by_instrument: Dict[str, List[int]] = {}
    for r in rooms:
        rooms_by_instrument.setdefault(r["instrument_type"], []).append(r["room_id"])

    for d_idx, day in enumerate(days):
        for s_idx, (start_time, end_time) in enumerate(slots):
            instrument = instruments[(d_idx + s_idx) % len(instruments)]
            instructor_id = instructor_for_instrument[instrument]
            student = students[(d_idx * len(slots) + s_idx) % len(students)]
            room_ids = rooms_by_instrument.get(instrument, [])
            room_id = room_ids[(d_idx + s_idx) % len(room_ids)] if room_ids else rooms[0]["room_id"]

            payload = {
                "instructor_id": instructor_id,
                "student_id": student["student_id"],
                "room_id": room_id,
                "instrument": instrument,
                "lesson_type": lesson_types[(d_idx + s_idx) % 2],
                "start_time": start_time,
                "end_time": end_time,
                "day_of_week": day,
                "term": term,
                "status": "scheduled",
            }

            # deterministic idempotent lookup
            lookup = {
                "term": term,
                "day_of_week": day,
                "start_time": start_time,
                "instructor_id": instructor_id,
                "student_id": student["student_id"],
                "room_id": room_id,
            }

            _upsert_by_filter("lesson", lookup, payload)


def main():
    instructors = seed_instructors()
    students = seed_students()
    rooms = seed_rooms()

    seed_instructor_skills(instructors)
    seed_student_skills(students)
    seed_lessons(instructors, students, rooms)

    print("Seed complete:")
    print("- 5 instructors")
    print("- 15 students")
    print("- 7 rooms")
    print("- sample skills in instructor_skill and student_skill")
    print("- 25 lessons")
    print("Idempotent: safe to re-run.")


if __name__ == "__main__":
    main()