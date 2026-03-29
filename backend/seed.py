"""
Seed script — clears all tables then populates Supabase with sample data.

Run from the project root:
    PYTHONPATH=. python backend/seed.py

Login credentials seeded:
    username: barnes   password: password
    username: admin    password: admin123

Tables populated (in order):
    app_user → person → client → room → instructor → student → lesson → lesson_enrollment

A person can hold both a student role and a client role:
  - Felix Nguyen is an adult student (student only)
  - Linda Chen is a parent/guardian (client only)
  - Marcus Webb takes lessons himself AND manages his daughter's enrolment (student + client)
"""

import hashlib
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from backend.app.infrastructure.database.database import DatabaseConnection

db = DatabaseConnection().client


# ── Helpers ───────────────────────────────────────────────────────────────────

def insert(table, rows):
    result = db.table(table).insert(rows).execute()
    print(f"  + {table}: inserted {len(result.data)} row(s)")
    return result.data


def clear(table):
    db.table(table).delete().neq("created_at", "1970-01-01").execute()


def clear_no_ts(table, pk):
    """Clear tables that have no created_at — delete all rows via pk not null."""
    db.table(table).delete().not_.is_(pk, "null").execute()


def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()


# ── Seed ──────────────────────────────────────────────────────────────────────

def seed():
    print("\n-- Clearing existing data --")
    # Delete in reverse dependency order
    for t, pk in [
        ("audit_log",          "log_id"),
        ("credit_transaction", "transaction_id"),
        ("payment",            "payment_id"),
        ("invoice_line",       "line_id"),
        ("invoice",            "invoice_id"),
        ("lesson_enrollment",  "enrollment_id"),
        ("lesson",             "lesson_id"),
        ("student",            "student_id"),
        ("client",             "client_id"),
        ("instructor",         "instructor_id"),
        ("room",               "room_id"),
        ("skill",              "skill_id"),
        ("attendance_policy",  "policy_id"),
        ("person",             "person_id"),
        ("app_user",           "user_id"),
    ]:
        try:
            db.table(t).delete().not_.is_(pk, "null").execute()
            print(f"  - cleared {t}")
        except Exception:
            pass  # table may be empty already

    print("\n-- Seeding database --")

    # ── App users ─────────────────────────────────────────────────────────────
    print("\n[1/8] App users")
    insert("app_user", [
        {"username": "barnes", "password_hash": sha256("password"), "role": "admin"},
        {"username": "admin",  "password_hash": sha256("admin123"), "role": "admin"},
    ])

    # ── Attendance policies ───────────────────────────────────────────────────
    print("\n[2/8] Attendance policies")
    insert("attendance_policy", [
        {
            "name":                    "Standard",
            "absent_charge_type":      "percentage",
            "absent_charge_value":     50,
            "cancel_charge_type":      "none",
            "cancel_charge_value":     0,
            "late_cancel_charge_type": "flat",
            "late_cancel_charge_value": 25,
            "is_default":              True,
        },
    ])

    # ── Persons (shared identity) ─────────────────────────────────────────────
    print("\n[3/8] Persons")
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
    print("\n[4/8] Clients")
    clients_data = [
        {"person_id": p["Linda Chen"]},
        {"person_id": p["Robert Martin"]},
        {"person_id": p["Hana Diaz"]},
        {"person_id": p["Marcus Webb"]},
    ]
    clients = insert("client", clients_data)
    c = {
        "Linda Chen":    clients[0]["client_id"],
        "Robert Martin": clients[1]["client_id"],
        "Hana Diaz":     clients[2]["client_id"],
        "Marcus Webb":   clients[3]["client_id"],
    }

    # ── Rooms ─────────────────────────────────────────────────────────────────
    print("\n[5/8] Rooms")
    rooms = insert("room", [
        {"name": "Studio A",     "capacity": 5},
        {"name": "Studio B",     "capacity": 3},
        {"name": "Recital Hall", "capacity": 20},
    ])
    r = {rm["name"]: rm["room_id"] for rm in rooms}

    # ── Instructors ───────────────────────────────────────────────────────────
    print("\n[6/8] Instructors")
    instructors = insert("instructor", [
        {"name": "Sarah Mills", "email": "sarah@musicdepot.ca", "phone": "416-555-0101"},
        {"name": "James Park",  "email": "james@musicdepot.ca", "phone": "416-555-0102"},
        {"name": "Yuki Tanaka", "email": "yuki@musicdepot.ca",  "phone": "416-555-0103"},
    ])
    i = {inst["name"]: inst["instructor_id"] for inst in instructors}

    # ── Students ──────────────────────────────────────────────────────────────
    print("\n[7/8] Students")
    students_data = [
        {"person_id": p["Alice Chen"],   "client_id": c["Linda Chen"]},
        {"person_id": p["Bob Chen"],     "client_id": c["Linda Chen"]},
        {"person_id": p["Clara Martin"], "client_id": c["Robert Martin"]},
        {"person_id": p["David Diaz"],   "client_id": c["Hana Diaz"]},
        {"person_id": p["Emma Diaz"],    "client_id": c["Hana Diaz"]},
        {"person_id": p["Felix Nguyen"], "client_id": None},
        {"person_id": p["Marcus Webb"],  "client_id": None},
        {"person_id": p["Olivia Webb"],  "client_id": c["Marcus Webb"]},
    ]
    students = insert("student", students_data)
    s = {}
    for st in students:
        for name, pid in p.items():
            if st["person_id"] == pid:
                s[name] = st["student_id"]
                break

    # ── Lessons (dates in current week / recent weeks for calendar visibility) ─
    print("\n[8/8] Lessons + enrollments")
    lessons_data = [
        {
            "instructor_id": i["Sarah Mills"],
            "room_id":        r["Studio A"],
            "start_time":     "2026-03-30T10:00:00",
            "end_time":       "2026-03-30T11:00:00",
            "rate":           60.0,
            "status":         "Scheduled",
            "recurrence":     "0 10 * * 1",
        },
        {
            "instructor_id": i["James Park"],
            "room_id":        r["Studio B"],
            "start_time":     "2026-04-01T14:00:00",
            "end_time":       "2026-04-01T15:00:00",
            "rate":           55.0,
            "status":         "Scheduled",
            "recurrence":     "0 14 * * 3",
        },
        {
            "instructor_id": i["Yuki Tanaka"],
            "room_id":        r["Recital Hall"],
            "start_time":     "2026-04-03T09:00:00",
            "end_time":       "2026-04-03T10:30:00",
            "rate":           50.0,
            "status":         "Scheduled",
            "recurrence":     "0 9 * * 5",
        },
        {
            "instructor_id": i["Sarah Mills"],
            "room_id":        r["Studio A"],
            "start_time":     "2026-03-23T10:00:00",
            "end_time":       "2026-03-23T11:00:00",
            "rate":           60.0,
            "status":         "Completed",
            "recurrence":     "0 10 * * 1",
        },
        {
            "instructor_id": i["James Park"],
            "room_id":        r["Studio B"],
            "start_time":     "2026-03-31T11:00:00",
            "end_time":       "2026-03-31T12:00:00",
            "rate":           55.0,
            "status":         "Scheduled",
            "recurrence":     None,
        },
    ]
    lessons = insert("lesson", lessons_data)
    lid = [l["lesson_id"] for l in lessons]

    insert("lesson_enrollment", [
        {"lesson_id": lid[0], "student_id": s["Alice Chen"]},
        {"lesson_id": lid[0], "student_id": s["Bob Chen"]},
        {"lesson_id": lid[1], "student_id": s["Clara Martin"]},
        {"lesson_id": lid[1], "student_id": s["David Diaz"]},
        {"lesson_id": lid[2], "student_id": s["Alice Chen"]},
        {"lesson_id": lid[2], "student_id": s["Emma Diaz"]},
        {"lesson_id": lid[2], "student_id": s["Felix Nguyen"]},
        {"lesson_id": lid[2], "student_id": s["Marcus Webb"]},
        {"lesson_id": lid[2], "student_id": s["Olivia Webb"]},
        {"lesson_id": lid[3], "student_id": s["Alice Chen"]},
        {"lesson_id": lid[3], "student_id": s["Bob Chen"]},
        {"lesson_id": lid[4], "student_id": s["Felix Nguyen"]},
    ])

    print("\n-- Done --")
    print("\nLogin: barnes / password  or  admin / admin123\n")


if __name__ == "__main__":
    seed()
