"""
Your Music Depot — Seed Script
================================
Generates realistic 5-year history for a music school.

  20  instructors (+ person records)
   8  rooms
   2  attendance policies
 100  clients   (+ person records)
 500  students  (+ person records, ~5 per client)
  40  lesson templates  (20 private · 20 group)
  ~11 500  lesson occurrences  (weekly, 2021-04 → 2026-09)
  ~65 000  lesson enrollments
  ~6 000   invoices  (last 24 months)
  ~20 000  invoice line items
  ~4 500   credit transactions (paid invoices)

Usage (from the project root):
    python backend/seed.py              # seed (skips if data already exists)
    python backend/seed.py --clear      # wipe all tables, then seed

Login credentials seeded:
    username: admin    password: password
    username: barnes   password: password
"""

import os
import sys
import uuid
import random
import calendar
import hashlib
from datetime import date, timedelta
from collections import defaultdict

# ── Path + env ────────────────────────────────────────────────────────────────
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from backend.app.infrastructure.database.database import DatabaseConnection
db = DatabaseConnection().client


# ── Parameters ────────────────────────────────────────────────────────────────
SEED_START    = date(2021, 4,  1)
SEED_END      = date(2026, 9, 30)
TODAY         = date(2026, 3, 29)
INVOICE_FROM  = date(2024, 4,  1)   # invoices generated for the last ~24 months

N_INSTRUCTORS     = 20
N_ROOMS           = 8
N_CLIENTS         = 100
N_STUDENTS        = 500
N_PRIVATE_LESSONS = 20   # 2–3 students each
N_GROUP_LESSONS   = 20   # 6–12 students each

BATCH_SIZE = 500


# ── Reference data ────────────────────────────────────────────────────────────
FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
    "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia",
    "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Michael",
    "Emily", "Elijah", "Elizabeth", "Daniel", "Sofia", "Matthew", "Avery",
    "Jackson", "Ella", "Sebastian", "Scarlett", "David", "Grace", "Carter",
    "Victoria", "Jayden", "Riley", "Luke", "Aria", "John", "Lily", "Dylan",
    "Aubrey", "Logan", "Zoey", "Ryan", "Penelope", "Owen", "Layla", "Nathan",
    "Chloe", "Jack", "Nora", "Connor", "Hannah", "Tyler", "Lillian", "Isaac",
    "Addison", "Hunter", "Paisley", "Andrew", "Aurora", "Justin", "Brooklyn",
    "Christian", "Savannah", "Brayden", "Ellie", "Wyatt", "Anna", "Julian",
    "Natalie", "Gavin", "Leah", "Caleb", "Hazel", "Levi", "Violet", "Evan",
    "Stella", "Oliver", "Zoe", "Jordan", "Mila", "Ian", "Eleanor", "Miles",
    "Luna", "Kyle", "Caroline", "Zachary", "Naomi", "Nolan", "Audrey", "Cole",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Li", "Chen", "Patel", "Kim", "Singh", "Khan",
    "Ahmed", "Ali", "Cohen", "Levy", "Kumar", "Zhang", "Wang", "Liu",
    "Yang", "Huang", "Zhao", "Wu", "Sun", "Reed", "Murphy", "Bailey",
    "Cooper", "Richardson", "Cox", "Ward", "Peterson", "Howard", "Turner",
    "Collins", "Stewart", "Morris", "Rogers", "Cook", "Morgan", "Bell",
    "Gomez", "Kelly", "Hughes", "Foster", "Barnes", "Wells", "Long",
    "Owens", "Simmons", "Ross", "Fisher", "Jordan", "Coleman", "Ramos",
]

INSTRUMENTS = [
    "Piano", "Guitar", "Violin", "Drums", "Voice", "Bass Guitar",
    "Cello", "Flute", "Clarinet", "Trumpet", "Saxophone", "Viola",
]

INSTRUMENT_FAMILIES = {
    "Piano": "keyboard", "Guitar": "strings", "Violin": "strings",
    "Drums": "percussion", "Voice": "voice", "Bass Guitar": "strings",
    "Cello": "strings", "Flute": "woodwind", "Clarinet": "woodwind",
    "Trumpet": "brass", "Saxophone": "woodwind", "Viola": "strings",
}

SKILL_LEVELS = ["beginner", "elementary", "intermediate", "advanced", "professional"]
SKILL_WEIGHTS = [30, 30, 20, 12, 8]

ROOM_NAMES = [
    "Studio A", "Studio B", "Studio C", "Studio D",
    "Practice Room 1", "Practice Room 2", "Recital Hall", "Recording Suite",
]

DOW_CRON   = {0: "MON", 1: "TUE", 2: "WED", 3: "THU", 4: "FRI"}
DOW_PARSE  = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4}

START_HOURS = [9, 10, 11, 13, 14, 15, 16, 17]
DURATIONS   = [30, 45, 60, 90]     # minutes

ISSUERS = [
    "RCM", "Toronto Conservatory", "ORMTA", "College of Music", "Berklee Online",
]

COMPAT_REASONS = [
    "Student request", "Instructor preference", "Parent request",
    "Teaching style mismatch", "Safeguarding note", "Scheduling history",
]

PAYMENT_METHODS = ["Card", "Cash", "E-Transfer", "Cheque"]

AREA_CODES = ["416", "647", "905", "519", "613"]


# ── Utilities ─────────────────────────────────────────────────────────────────
def nid() -> str:
    return str(uuid.uuid4())


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def rand_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def rand_email(name: str) -> str:
    parts = name.lower().replace("-", "").split()
    return f"{parts[0]}.{parts[-1]}{random.randint(1, 99)}@example.com"


def rand_phone() -> str:
    ac = random.choice(AREA_CODES)
    return f"{ac}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def add_minutes(hhmm: str, mins: int) -> str:
    h, m = map(int, hhmm.split(":"))
    t = h * 60 + m + mins
    return f"{(t // 60) % 24:02d}:{t % 60:02d}"


def weekly_dates(weekday: int, start: date, end: date) -> list:
    """All dates matching weekday between start and end (inclusive)."""
    dates, cur = [], start
    while cur.weekday() != weekday:
        cur += timedelta(days=1)
    while cur <= end:
        dates.append(cur)
        cur += timedelta(weeks=1)
    return dates


def month_end(year: int, month: int) -> date:
    return date(year, month, calendar.monthrange(year, month)[1])


def charge_for(rate: float, att) -> float:
    """Simplified charge calculation matching the Standard attendance policy."""
    if att == "Excused":
        return 0.0
    if att == "Absent":
        return round(rate * 0.5, 2)
    if att == "Late Cancel":
        return min(25.0, rate)
    return rate   # Present or None → full rate


def batch_insert(table: str, rows: list, label: str = ""):
    if not rows:
        return
    tag = label or table
    batches = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
    for idx in range(batches):
        chunk = rows[idx * BATCH_SIZE:(idx + 1) * BATCH_SIZE]
        try:
            db.table(table).insert(chunk).execute()
        except Exception as exc:
            print(f"  ! {tag} batch {idx + 1}/{batches}: {exc}")
    print(f"  OK {tag}: {len(rows):,} rows")


# ── Clear ─────────────────────────────────────────────────────────────────────
_CLEAR_ORDER = [
    ("audit_log",                        "log_id"),
    ("credit_transaction",               "transaction_id"),
    ("payment",                          "payment_id"),
    ("invoice_line",                     "line_id"),
    ("invoice",                          "invoice_id"),
    ("instructor_student_compatibility", "compatibility_id"),
    ("credential",                       "credential_id"),
    ("lesson_enrollment",                "enrollment_id"),
    ("lesson_occurrence",                "occurrence_id"),
    ("lesson",                           "lesson_id"),
    ("course",                           "course_id"),
    ("student",                          "student_id"),
    ("client",                           "client_id"),
    ("attendance_policy",                "policy_id"),
    ("skill",                            "skill_id"),
    ("room",                             "room_id"),
    ("instructor",                       "instructor_id"),
    ("person",                           "person_id"),
    ("app_user",                         "user_id"),
]

NIL = "00000000-0000-0000-0000-000000000000"


def clear_all():
    print("Clearing all tables…")
    for table, pk in _CLEAR_ORDER:
        try:
            db.table(table).delete().neq(pk, NIL).execute()
            print(f"  cleared {table}")
        except Exception as exc:
            print(f"  ! {table}: {exc}")


# ── Check if already seeded ───────────────────────────────────────────────────
def already_seeded() -> bool:
    try:
        result = db.table("person").select("person_id", count="exact").limit(1).execute()
        return (result.count or 0) > 0
    except Exception:
        return False


# ── Seed functions ────────────────────────────────────────────────────────────

def seed_app_users():
    print("\n[1] App users")
    pw = sha256("password")
    rows = [
        {"username": "admin",  "password_hash": pw, "role": "admin"},
        {"username": "barnes", "password_hash": pw, "role": "admin"},
    ]
    batch_insert("app_user", rows, "app_user")


def seed_policies():
    print("\n[2] Attendance policies")
    batch_insert("attendance_policy", [
        {
            "name": "Standard",
            "absent_charge_type": "percentage", "absent_charge_value": 50,
            "cancel_charge_type": "none",        "cancel_charge_value": 0,
            "late_cancel_charge_type": "flat",   "late_cancel_charge_value": 25,
            "is_default": True,
        },
        {
            "name": "Strict",
            "absent_charge_type": "percentage", "absent_charge_value": 100,
            "cancel_charge_type": "percentage", "cancel_charge_value": 50,
            "late_cancel_charge_type": "flat",  "late_cancel_charge_value": 40,
            "is_default": False,
        },
    ], "attendance_policy")


def seed_instructors(n: int) -> list:
    print(f"\n[3] Instructors ({n})")
    persons, instructors = [], []
    for _ in range(n):
        pid, iid = nid(), nid()
        name = rand_name()
        persons.append({
            "person_id": pid, "name": name,
            "email": rand_email(name), "phone": rand_phone(),
        })
        instructors.append({
            "instructor_id": iid,
            "person_id":     pid,
            "hourly_rate":   round(random.uniform(45, 120), 2),
            "blocked_times": [],
            "restrictions":  [],
        })
    batch_insert("person",     persons,     "person (instructors)")
    batch_insert("instructor", instructors, "instructor")
    return instructors


def seed_rooms(n: int) -> list:
    print(f"\n[4] Rooms ({n})")
    rooms = []
    for i in range(n):
        instruments = random.sample(INSTRUMENTS, random.randint(1, 3))
        rooms.append({
            "room_id":  nid(),
            "name":     ROOM_NAMES[i % len(ROOM_NAMES)],
            "capacity": random.choice([4, 6, 8, 10, 15, 20]),
            "instruments": [
                {"name": inst, "quantity": random.randint(1, 3)}
                for inst in instruments
            ],
            "blocked_times": [],
        })
    batch_insert("room", rooms, "room")
    return rooms


def seed_clients_and_students(n_clients: int, n_students: int) -> tuple:
    print(f"\n[5] Clients ({n_clients}) + Students ({n_students})")

    # Clients
    cpersons, clients = [], []
    for _ in range(n_clients):
        pid, cid = nid(), nid()
        name = rand_name()
        cpersons.append({
            "person_id": pid, "name": name,
            "email": rand_email(name), "phone": rand_phone(),
        })
        clients.append({
            "client_id": cid, "person_id": pid,
            "credits": round(random.uniform(0, 300), 2),
            "blocked_times": [],
        })
    batch_insert("person", cpersons, "person (clients)")
    batch_insert("client", clients,  "client")

    # Students
    spersons, students = [], []
    for _ in range(n_students):
        pid, sid = nid(), nid()
        name = rand_name()
        spersons.append({
            "person_id": pid, "name": name,
            "email": rand_email(name), "phone": rand_phone(),
        })
        # Each student plays 1-3 instruments at various skill levels
        num_instruments = random.randint(1, 3)
        student_instruments = random.sample(INSTRUMENTS, num_instruments)
        isl = [
            {
                "name": inst,
                "family": INSTRUMENT_FAMILIES[inst],
                "skill_level": random.choices(SKILL_LEVELS, weights=SKILL_WEIGHTS)[0],
            }
            for inst in student_instruments
        ]
        students.append({
            "student_id":              sid,
            "person_id":               pid,
            "client_id":               random.choice(clients)["client_id"],
            "instrument_skill_levels": isl,
            "age":                     random.randint(6, 65),
            "requirements":            [],
        })
    batch_insert("person",  spersons, "person (students)")
    batch_insert("student", students, "student")

    return clients, students


def seed_credentials(instructors: list):
    print("\n[6] Credentials")
    cred_types = ["musical", "cpr", "special_ed", "vulnerable_sector", "first_aid"]
    creds = []
    for inst in instructors:
        n = random.randint(1, 3)
        for ctype in random.sample(cred_types, n):
            vf = SEED_START + timedelta(days=random.randint(0, 180))
            vu = TODAY + timedelta(days=random.randint(90, 900))
            profs = []
            if ctype == "musical":
                instr   = random.choice(INSTRUMENTS)
                max_lvl = random.choice(SKILL_LEVELS)
                profs   = [{"instrument": instr, "min_level": "beginner", "max_level": max_lvl}]
            creds.append({
                "credential_id":   nid(),
                "instructor_id":   inst["instructor_id"],
                "credential_type": ctype,
                "proficiencies":   profs,
                "valid_from":      vf.isoformat(),
                "valid_until":     vu.isoformat(),
                "issued_by":       random.choice(ISSUERS),
                "issued_date":     vf.isoformat(),
            })
    batch_insert("credential", creds, "credential")


def seed_compatibility(instructors: list, students: list):
    print("\n[7] Instructor-student compatibility")
    verdicts   = ["blocked", "disliked", "preferred", "required"]
    v_weights  = [5, 15, 60, 20]
    initiators = ["student", "instructor", "admin"]
    rows, seen = [], set()
    for _ in range(80):
        iid = random.choice(instructors)["instructor_id"]
        sid = random.choice(students)["student_id"]
        if (iid, sid) in seen:
            continue
        seen.add((iid, sid))
        rows.append({
            "compatibility_id": nid(),
            "instructor_id":    iid,
            "student_id":       sid,
            "verdict":          random.choices(verdicts, weights=v_weights)[0],
            "reason":           random.choice(COMPAT_REASONS),
            "initiated_by":     random.choice(initiators),
        })
    batch_insert("instructor_student_compatibility", rows, "compatibility")


def seed_lessons_occurrences_enrollments_invoices(
    instructors: list,
    rooms: list,
    students: list,
):
    print(f"\n[8] Lessons, occurrences, enrollments + invoices")

    # ── Build lesson templates ────────────────────────────────────────────────
    n_lessons  = N_PRIVATE_LESSONS + N_GROUP_LESSONS
    all_sids   = [s["student_id"] for s in students]
    random.shuffle(all_sids)
    pool_idx   = 0

    lessons:         list = []
    lesson_enrolled: dict = {}   # lesson_id → [student_id, …]

    for i in range(n_lessons):
        lid      = nid()
        weekday  = random.randint(0, 4)
        hour     = random.choice(START_HOURS)
        dur      = random.choice(DURATIONS)
        start_t  = f"{hour:02d}:00"
        end_t    = add_minutes(start_t, dur)
        rate     = round(random.uniform(30, 85), 2)
        cron     = f"0 {hour} * * {DOW_CRON[weekday]}"

        is_group = i >= N_PRIVATE_LESSONS
        n_enroll = random.randint(6, 12) if is_group else random.randint(2, 3)
        enrolled = []
        for _ in range(n_enroll):
            if pool_idx < len(all_sids):
                enrolled.append(all_sids[pool_idx])
                pool_idx += 1
            else:
                enrolled.append(random.choice(all_sids))

        lesson_enrolled[lid] = enrolled
        lessons.append({
            "lesson_id":     lid,
            "instructor_id": random.choice(instructors)["instructor_id"],
            "room_id":       random.choice(rooms)["room_id"],
            "course_id":     None,
            "start_time":    start_t,
            "end_time":      end_t,
            "student_ids":   enrolled,
            "rate":          rate,
            "status":        "active",
            "recurrence":    cron,
        })

    batch_insert("lesson", lessons, "lesson")

    # ── Generate occurrences + enrollments ────────────────────────────────────
    all_occurrences: list = []
    all_enrollments: list = []

    # invoice buckets: (student_id, year, month) → [{occurrence_id, description, amount, att}]
    inv_buckets: dict = defaultdict(list)

    three_months_ago = date(
        TODAY.year if TODAY.month > 3 else TODAY.year - 1,
        (TODAY.month - 3) % 12 or 12, 1,
    )

    print("  Building occurrences and enrollments in memory…")
    for lesson in lessons:
        lid      = lesson["lesson_id"]
        weekday  = DOW_PARSE[lesson["recurrence"].split()[-1]]
        enrolled = lesson_enrolled[lid]
        dates    = weekly_dates(weekday, SEED_START, SEED_END)

        for d in dates:
            oid     = nid()
            is_past = d < TODAY

            if is_past:
                status = random.choices(
                    ["Completed", "Cancelled"], weights=[92, 8]
                )[0]
            else:
                status = "Scheduled"

            all_occurrences.append({
                "occurrence_id":   oid,
                "lesson_id":       lid,
                "course_id":       None,
                "date":            d.isoformat(),
                "start_time":      lesson["start_time"],
                "end_time":        lesson["end_time"],
                "instructor_id":   lesson["instructor_id"],
                "room_id":         lesson["room_id"],
                "status":          status,
                "rate":            lesson["rate"],
                "is_rescheduled":  False,
                "cancelled_reason": None,
            })

            for sid in enrolled:
                if status == "Completed":
                    att = random.choices(
                        ["Present", "Absent", "Late Cancel", "Excused"],
                        weights=[84, 8, 6, 2],
                    )[0]
                elif status == "Cancelled":
                    att = "Cancelled"
                else:
                    att = None   # future Scheduled — no attendance yet

                all_enrollments.append({
                    "enrollment_id":    nid(),
                    "occurrence_id":    oid,
                    "student_id":       sid,
                    "attendance_status": att,
                })

                # Collect for invoice generation
                if (
                    status == "Completed"
                    and is_past
                    and d >= INVOICE_FROM
                    and att != "Cancelled"
                ):
                    amt = charge_for(lesson["rate"], att)
                    inv_buckets[(sid, d.year, d.month)].append({
                        "occurrence_id":    oid,
                        "description":      f"{att or 'Present'} — {d.isoformat()}",
                        "amount":           amt,
                        "attendance_status": att,
                    })

    print(f"  {len(all_occurrences):,} occurrences · {len(all_enrollments):,} enrollments")
    batch_insert("lesson_occurrence", all_occurrences, "lesson_occurrence")
    batch_insert("lesson_enrollment", all_enrollments, "lesson_enrollment")

    # ── Generate invoices, lines, transactions ────────────────────────────────
    student_client = {s["student_id"]: s["client_id"] for s in students}

    invoices:     list = []
    lines:        list = []
    transactions: list = []

    for (sid, yr, mo), items in inv_buckets.items():
        if not items:
            continue
        inv_id   = nid()
        p_start  = date(yr, mo, 1)
        p_end    = month_end(yr, mo)
        total    = round(sum(it["amount"] for it in items), 2)
        cid      = student_client.get(sid)

        if p_end < three_months_ago:
            status = random.choices(["Paid", "Overdue"], weights=[90, 10])[0]
        else:
            status = random.choices(["Paid", "Pending"], weights=[55, 45])[0]

        amount_paid = total if status == "Paid" else 0.0

        invoices.append({
            "invoice_id":   inv_id,
            "student_id":   sid,
            "client_id":    cid,
            "period_start": p_start.isoformat(),
            "period_end":   p_end.isoformat(),
            "total_amount": total,
            "amount_paid":  amount_paid,
            "status":       status,
        })

        for it in items:
            lines.append({
                "line_id":           nid(),
                "invoice_id":        inv_id,
                "occurrence_id":     it["occurrence_id"],
                "item_type":         "lesson",
                "description":       it["description"],
                "amount":            it["amount"],
                "attendance_status": it["attendance_status"],
            })

        if status == "Paid" and cid:
            transactions.append({
                "transaction_id": nid(),
                "client_id":      cid,
                "invoice_id":     inv_id,
                "amount":         -total,   # negative = credit spent
                "reason":         f"Invoice payment {p_start.strftime('%b %Y')}",
                "payment_method": random.choice(PAYMENT_METHODS),
            })

    print(f"  {len(invoices):,} invoices · {len(lines):,} lines · {len(transactions):,} transactions")
    batch_insert("invoice",            invoices,     "invoice")
    batch_insert("invoice_line",       lines,        "invoice_line")
    batch_insert("credit_transaction", transactions, "credit_transaction")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Seed Your Music Depot")
    parser.add_argument(
        "--clear", action="store_true",
        help="Wipe all existing data before seeding (destructive)"
    )
    args = parser.parse_args()

    if args.clear:
        clear_all()
    elif already_seeded():
        print(
            "Database already contains data.\n"
            "Use --clear to wipe and re-seed, or run against a fresh project."
        )
        return

    print("\nSeeding Your Music Depot…")
    print("=" * 52)

    seed_app_users()
    seed_policies()
    instructors          = seed_instructors(N_INSTRUCTORS)
    rooms                = seed_rooms(N_ROOMS)
    clients, students    = seed_clients_and_students(N_CLIENTS, N_STUDENTS)
    seed_credentials(instructors)
    seed_compatibility(instructors, students)
    seed_lessons_occurrences_enrollments_invoices(instructors, rooms, students)

    print("\n" + "=" * 52)
    print("Seed complete.")
    print("  admin / password")
    print("  barnes / password")
    print()


if __name__ == "__main__":
    main()
