from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

from dotenv import load_dotenv
from supabase import Client, create_client


def _db() -> Client:
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    load_dotenv(env_path)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in backend/.env")
    return create_client(url, key)


def _fetch_rows(table: str) -> List[Dict[str, Any]]:
    return _db().table(table).select("*").execute().data or []


def _insert_rows(table: str, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not rows:
        return []
    return _db().table(table).insert(rows).execute().data or []


def _column_exists(table: str, column: str) -> bool:
    try:
        _db().table(table).select(column).limit(1).execute()
        return True
    except Exception:
        return False


def _first_existing_column(table: str, candidates: List[str]) -> str | None:
    for candidate in candidates:
        if _column_exists(table, candidate):
            return candidate
    return None


def _ensure_instructors(target_count: int = 5) -> List[Dict[str, Any]]:
    existing = _fetch_rows("instructor")
    needed = max(0, target_count - len(existing))
    if needed == 0:
        return existing

    seed_rows = []
    base = len(existing) + 1
    for i in range(needed):
        idx = base + i
        seed_rows.append(
            {
                "name": f"Instructor {idx}",
                "email": f"instructor{idx}@yourmusicdepot.test",
                "phone": f"555-210-{idx:04d}",
            }
        )

    _insert_rows("instructor", seed_rows)
    return _fetch_rows("instructor")


def _ensure_students(target_count: int = 15) -> List[Dict[str, Any]]:
    existing = _fetch_rows("student")
    needed = max(0, target_count - len(existing))
    if needed == 0:
        return existing

    seed_rows = []
    base = len(existing) + 1
    for i in range(needed):
        idx = base + i
        seed_rows.append(
            {
                "name": f"Student {idx}",
                "email": f"student{idx}@yourmusicdepot.test",
                "phone": f"555-310-{idx:04d}",
            }
        )

    _insert_rows("student", seed_rows)
    return _fetch_rows("student")


def _ensure_rooms(target_count: int = 7) -> List[Dict[str, Any]]:
    existing = _fetch_rows("room")
    needed = max(0, target_count - len(existing))
    if needed == 0:
        return existing

    seed_rows = []
    base = len(existing) + 1
    for i in range(needed):
        idx = base + i
        seed_rows.append(
            {
                "name": f"Studio {idx}",
                "capacity": 4 if idx % 3 == 0 else 2,
            }
        )

    _insert_rows("room", seed_rows)
    return _fetch_rows("room")


def _ensure_skills(instructors: List[Dict[str, Any]], students: List[Dict[str, Any]]) -> None:
    instruments = ["Piano", "Guitar", "Violin", "Drums", "Voice", "Bass"]
    instructor_skill_rows = _fetch_rows("instructor_skill")
    student_skill_rows = _fetch_rows("student_skill")

    instructor_skill_col = _first_existing_column("instructor_skill", ["skill", "instrument", "skill_name"])
    instructor_min_col = _first_existing_column("instructor_skill", ["min_skill_level", "minimum_skill_level", "min_level"])
    student_skill_col = _first_existing_column("student_skill", ["skill", "instrument", "skill_name"])
    student_level_col = _first_existing_column("student_skill", ["skill_level", "level", "student_skill_level"])

    if not instructor_skill_col or not instructor_min_col or not student_skill_col or not student_level_col:
        print("[WARN] skill columns could not be resolved; skipping skill seeding")
        return

    existing_i = {
        (row.get("instructor_id"), str(row.get(instructor_skill_col, "")).strip().lower())
        for row in instructor_skill_rows
    }
    existing_s = {
        (row.get("student_id"), str(row.get(student_skill_col, "")).strip().lower())
        for row in student_skill_rows
    }

    new_i: List[Dict[str, Any]] = []
    for idx, instructor in enumerate(instructors[:5]):
        instructor_id = instructor.get("instructor_id")
        if instructor_id is None:
            continue
        instrument = instruments[idx % len(instruments)]
        key = (instructor_id, instrument.lower())
        if key in existing_i:
            continue
        new_i.append(
            {
                "instructor_id": instructor_id,
                instructor_skill_col: instrument,
                instructor_min_col: (idx % 4) + 1,
            }
        )

    new_s: List[Dict[str, Any]] = []
    for idx, student in enumerate(students[:15]):
        student_id = student.get("student_id")
        if student_id is None:
            continue
        instrument = instruments[idx % len(instruments)]
        key = (student_id, instrument.lower())
        if key in existing_s:
            continue
        new_s.append(
            {
                "student_id": student_id,
                student_skill_col: instrument,
                student_level_col: ((idx + 2) % 5) + 1,
            }
        )

    _insert_rows("instructor_skill", new_i)
    _insert_rows("student_skill", new_s)


def _monday_of_current_week() -> datetime:
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    return datetime(monday.year, monday.month, monday.day, 0, 0, 0)


def _ensure_full_week_lessons(
    instructors: List[Dict[str, Any]],
    students: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
) -> int:
    if not instructors or not students or not rooms:
        return 0

    existing_lessons = _fetch_rows("lesson")
    per_day_counts: Dict[str, int] = {}
    for row in existing_lessons:
        day = str(row.get("day_of_week") or "").strip()
        if not day:
            continue
        per_day_counts[day] = per_day_counts.get(day, 0) + 1

    instruments = ["Piano", "Guitar", "Violin", "Drums", "Voice", "Bass"]
    lesson_rows: List[Dict[str, Any]] = []

    # Mon-Sat, 4 lessons/day. Saturday window is 9:00-15:00.
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for day_offset in range(6):
        day_name = day_names[day_offset]
        if per_day_counts.get(day_name, 0) >= 4:
            continue
        slots = [9, 10, 11, 13] if day_offset == 5 else [9, 11, 14, 16]
        for slot_idx, hour in enumerate(slots):
            start_hour = hour
            end_hour = hour + 1
            instructor = instructors[(day_offset * 4 + slot_idx) % len(instructors)]
            student = students[(day_offset * 4 + slot_idx) % len(students)]
            room = rooms[(day_offset * 4 + slot_idx) % len(rooms)]

            instructor_id = instructor.get("instructor_id")
            student_id = student.get("student_id")
            room_id = room.get("room_id")
            if instructor_id is None or student_id is None or room_id is None:
                continue

            instrument = instruments[(day_offset * 4 + slot_idx) % len(instruments)]
            lesson_rows.append(
                {
                    "instructor_id": instructor_id,
                    "student_id": student_id,
                    "room_id": room_id,
                    "instrument": instrument,
                    "lesson_type": "group" if slot_idx % 3 == 0 else "private",
                    "start_time": f"{start_hour:02d}:00:00",
                    "end_time": f"{end_hour:02d}:00:00",
                    "day_of_week": day_name,
                    "term": "Spring 2026",
                    "status": "Scheduled",
                }
            )

    inserted = _insert_rows("lesson", lesson_rows)

    # Enroll extra students for group lessons where lesson_enrollment exists.
    enrollment_rows: List[Dict[str, Any]] = []
    if inserted:
        student_ids = [s.get("student_id") for s in students if s.get("student_id") is not None]
        if student_ids:
            for idx, lesson in enumerate(inserted):
                if lesson.get("lesson_type") != "group":
                    continue
                lesson_id = lesson.get("lesson_id")
                if lesson_id is None:
                    continue
                extra_1 = student_ids[(idx + 1) % len(student_ids)]
                extra_2 = student_ids[(idx + 2) % len(student_ids)]
                enrollment_rows.append({"lesson_id": lesson_id, "student_id": extra_1})
                enrollment_rows.append({"lesson_id": lesson_id, "student_id": extra_2})

    if enrollment_rows:
        try:
            _insert_rows("lesson_enrollment", enrollment_rows)
        except Exception as exc:
            print(f"[WARN] lesson_enrollment seed skipped: {exc}")

    return len(inserted)


def main() -> None:
    instructors = _ensure_instructors(5)
    students = _ensure_students(15)
    rooms = _ensure_rooms(7)
    _ensure_skills(instructors, students)
    lessons_inserted = _ensure_full_week_lessons(instructors, students, rooms)

    print("Demo seeding complete")
    print(f"- instructors: {len(_fetch_rows('instructor'))}")
    print(f"- students: {len(_fetch_rows('student'))}")
    print(f"- rooms: {len(_fetch_rows('room'))}")
    print(f"- instructor_skill rows: {len(_fetch_rows('instructor_skill'))}")
    print(f"- student_skill rows: {len(_fetch_rows('student_skill'))}")
    print(f"- lessons inserted this run: {lessons_inserted}")


if __name__ == "__main__":
    main()
