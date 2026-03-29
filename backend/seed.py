"""
Seed script — populates Supabase with sample data.

Run from the project root:
    PYTHONPATH=. python backend/seed.py

Tables populated (in order):
    person → client → room → instructor → student → lesson → lesson_enrollment

A person can hold both a student role and a client role:
  - Felix Nguyen is an adult student (student only)
  - Linda Chen is a parent/guardian (client only)
  - Marcus Webb takes lessons himself AND manages his daughter's enrolment (student + client)
"""

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from backend.app.singletons.database import DatabaseConnection

db = DatabaseConnection().client


# ── Helpers ───────────────────────────────────────────────────────────────────

def insert(table, rows):
    result = db.table(table).insert(rows).execute()
    print(f"  ✓ {table}: inserted {len(result.data)} row(s)")
    return result.data


# ── Seed ──────────────────────────────────────────────────────────────────────

def seed():
    print("\n── Seeding database ─────────────────────────────────────────────")

    # ── Persons (shared identity) ─────────────────────────────────────────────
    print("\n[1/7] Persons")
    persons_data = [
        # parents / guardians (client role only)
        {"name": "Linda Chen",    "email": "linda@example.com",   "phone": "416-555-2001"},
        {"name": "Robert Martin", "email": "robert@example.com",  "phone": "416-555-2002"},
        {"name": "Hana Diaz",     "email": "hana@example.com",    "phone": "416-555-2003"},
        # adult student who also manages a child's enrolment (student + client)
        {"name": "Marcus Webb",   "email": "marcus@example.com",  "phone": "416-555-2004"},
        # students (student role only)
        {"name": "Alice Chen",    "email": "alice@example.com",   "phone": "416-555-1001"},
        {"name": "Bob Chen",      "email": "bob@example.com",     "phone": "416-555-1002"},
        {"name": "Clara Martin",  "email": "clara@example.com",   "phone": "416-555-1003"},
        {"name": "David Diaz",    "email": "david@example.com",   "phone": "416-555-1004"},
        {"name": "Emma Diaz",     "email": "emma@example.com",    "phone": "416-555-1005"},
        {"name": "Felix Nguyen",  "email": "felix@example.com",   "phone": "416-555-1006"},
        {"name": "Olivia Webb",   "email": "olivia@example.com",  "phone": "416-555-1007"},
    ]
    persons = insert("person", persons_data)
    p = {pr["name"]: pr["person_id"] for pr in persons}

    # ── Clients (billing / guardian role) ─────────────────────────────────────
    print("\n[2/7] Clients")
    clients_data = [
        {"person_id": p["Linda Chen"]},
        {"person_id": p["Robert Martin"]},
        {"person_id": p["Hana Diaz"]},
        {"person_id": p["Marcus Webb"]},   # also becomes a student below
    ]
    clients = insert("client", clients_data)
    c = {
        "Linda Chen":    clients[0]["client_id"],
        "Robert Martin": clients[1]["client_id"],
        "Hana Diaz":     clients[2]["client_id"],
        "Marcus Webb":   clients[3]["client_id"],
    }

    # ── Rooms ─────────────────────────────────────────────────────────────────
    print("\n[3/7] Rooms")
    rooms = insert("room", [
        {"name": "Studio A",    "capacity": 5},
        {"name": "Studio B",    "capacity": 3},
        {"name": "Recital Hall","capacity": 20},
    ])
    r = {rm["name"]: rm["room_id"] for rm in rooms}

    # ── Instructors ───────────────────────────────────────────────────────────
    print("\n[4/7] Instructors")
    instructors = insert("instructor", [
        {"name": "Sarah Mills", "email": "sarah@musicdepot.ca", "phone": "416-555-0101"},
        {"name": "James Park",  "email": "james@musicdepot.ca", "phone": "416-555-0102"},
        {"name": "Yuki Tanaka", "email": "yuki@musicdepot.ca",  "phone": "416-555-0103"},
    ])
    i = {inst["name"]: inst["instructor_id"] for inst in instructors}

    # ── Students (student role, linked to person + optional client) ───────────
    print("\n[5/7] Students")
    students_data = [
        # Linda Chen's kids
        {"person_id": p["Alice Chen"],   "client_id": c["Linda Chen"]},
        {"person_id": p["Bob Chen"],     "client_id": c["Linda Chen"]},
        # Robert Martin's kid
        {"person_id": p["Clara Martin"], "client_id": c["Robert Martin"]},
        # Hana Diaz's kids
        {"person_id": p["David Diaz"],   "client_id": c["Hana Diaz"]},
        {"person_id": p["Emma Diaz"],    "client_id": c["Hana Diaz"]},
        # Felix — adult, pays for himself (no client)
        {"person_id": p["Felix Nguyen"], "client_id": None},
        # Marcus Webb — adult student who also has a client account
        {"person_id": p["Marcus Webb"],  "client_id": None},
        # Olivia Webb — Marcus's daughter, billed to Marcus
        {"person_id": p["Olivia Webb"],  "client_id": c["Marcus Webb"]},
    ]
    students = insert("student", students_data)
    s = {}
    for st in students:
        # resolve person name from our map for easy lookup
        for name, pid in p.items():
            if st["person_id"] == pid:
                s[name] = st["student_id"]
                break

    # ── Lessons ───────────────────────────────────────────────────────────────
    # recurrence uses cron syntax: "MIN HOUR * * DOW"
    print("\n[6/7] Lessons")
    lessons_data = [
        {
            "instructor_id": i["Sarah Mills"],
            "room_id":        r["Studio A"],
            "start_time":     "2025-09-08T10:00:00",
            "end_time":       "2025-09-08T11:00:00",
            "rate":           60.0,
            "status":         "Scheduled",
            "recurrence":     "0 10 * * 1",   # every Monday 10:00
        },
        {
            "instructor_id": i["James Park"],
            "room_id":        r["Studio B"],
            "start_time":     "2025-09-10T14:00:00",
            "end_time":       "2025-09-10T15:00:00",
            "rate":           55.0,
            "status":         "Scheduled",
            "recurrence":     "0 14 * * 3",   # every Wednesday 14:00
        },
        {
            "instructor_id": i["Yuki Tanaka"],
            "room_id":        r["Recital Hall"],
            "start_time":     "2025-09-12T09:00:00",
            "end_time":       "2025-09-12T10:30:00",
            "rate":           50.0,
            "status":         "Scheduled",
            "recurrence":     "0 9 * * 5",    # every Friday 09:00
        },
        {
            "instructor_id": i["Sarah Mills"],
            "room_id":        r["Studio A"],
            "start_time":     "2025-09-15T10:00:00",
            "end_time":       "2025-09-15T11:00:00",
            "rate":           60.0,
            "status":         "Completed",
            "recurrence":     "0 10 * * 1",
        },
        {
            "instructor_id": i["James Park"],
            "room_id":        r["Studio B"],
            "start_time":     "2025-09-20T11:00:00",
            "end_time":       "2025-09-20T12:00:00",
            "rate":           55.0,
            "status":         "Scheduled",
            "recurrence":     None,            # one-off
        },
    ]
    lessons = insert("lesson", lessons_data)
    lid = [l["lesson_id"] for l in lessons]

    # ── Enrollments ───────────────────────────────────────────────────────────
    print("\n[7/7] Lesson enrollments")
    insert("lesson_enrollment", [
        # Lesson 0 — Mon Studio A: Alice + Bob (siblings)
        {"lesson_id": lid[0], "student_id": s["Alice Chen"]},
        {"lesson_id": lid[0], "student_id": s["Bob Chen"]},

        # Lesson 1 — Wed Studio B: Clara + David
        {"lesson_id": lid[1], "student_id": s["Clara Martin"]},
        {"lesson_id": lid[1], "student_id": s["David Diaz"]},

        # Lesson 2 — Fri Recital Hall: group class
        {"lesson_id": lid[2], "student_id": s["Alice Chen"]},
        {"lesson_id": lid[2], "student_id": s["Emma Diaz"]},
        {"lesson_id": lid[2], "student_id": s["Felix Nguyen"]},
        {"lesson_id": lid[2], "student_id": s["Marcus Webb"]},   # Marcus attends too
        {"lesson_id": lid[2], "student_id": s["Olivia Webb"]},   # as does his daughter

        # Lesson 3 — completed Mon (same series)
        {"lesson_id": lid[3], "student_id": s["Alice Chen"]},
        {"lesson_id": lid[3], "student_id": s["Bob Chen"]},

        # Lesson 4 — one-off: Felix only
        {"lesson_id": lid[4], "student_id": s["Felix Nguyen"]},
    ])

    print("\n── Done ─────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    seed()
