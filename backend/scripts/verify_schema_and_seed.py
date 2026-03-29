from __future__ import annotations

import os
import sys

from typing import Any, Dict, Optional, Tuple
from dotenv import load_dotenv
from supabase import Client, create_client


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def _db() -> Client:
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    load_dotenv(env_path)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in backend/.env")
    return create_client(url, key)


def _check_table_exists(table_name: str) -> Tuple[bool, str]:
    try:
        _db().table(table_name).select("*").limit(1).execute()
        return True, "ok"
    except Exception as exc:
        return False, str(exc)


def _check_column_exists(table_name: str, column_name: str) -> Tuple[bool, str]:
    try:
        _db().table(table_name).select(column_name).limit(1).execute()
        return True, "ok"
    except Exception as exc:
        return False, str(exc)


def _get_first_id(table_name: str, id_column: str) -> Optional[int]:
    try:
        rows = _db().table(table_name).select(id_column).limit(1).execute().data or []
        if not rows:
            return None
        value = rows[0].get(id_column)
        return int(value) if value is not None else None
    except Exception:
        return None


def _count_rows(table_name: str) -> Optional[int]:
    try:
        response = _db().table(table_name).select("*", count="exact").limit(1).execute()
        return int(response.count or 0)
    except Exception:
        return None


def _seed_instructor_skill_if_empty() -> Dict[str, Any]:
    table = "instructor_skill"
    exists, detail = _check_table_exists(table)
    if not exists:
        return {"seeded": False, "reason": f"table missing: {detail}"}

    count = _count_rows(table)
    if count is None:
        return {"seeded": False, "reason": "could not read row count"}
    if count > 0:
        return {"seeded": False, "reason": f"already has {count} row(s)"}

    instructor_id = _get_first_id("instructor", "instructor_id")
    if instructor_id is None:
        return {"seeded": False, "reason": "no instructor rows available"}

    payload = {
        "instructor_id": instructor_id,
        "skill": "Piano",
        "min_skill_level": 1,
    }
    try:
        _db().table(table).insert(payload).execute()
        return {"seeded": True, "payload": payload}
    except Exception as exc:
        return {"seeded": False, "reason": f"insert failed: {exc}"}


def _seed_student_skill_if_empty() -> Dict[str, Any]:
    table = "student_skill"
    exists, detail = _check_table_exists(table)
    if not exists:
        return {"seeded": False, "reason": f"table missing: {detail}"}

    count = _count_rows(table)
    if count is None:
        return {"seeded": False, "reason": "could not read row count"}
    if count > 0:
        return {"seeded": False, "reason": f"already has {count} row(s)"}

    student_id = _get_first_id("student", "student_id")
    if student_id is None:
        return {"seeded": False, "reason": "no student rows available"}

    payload = {
        "student_id": student_id,
        "skill": "Piano",
        "skill_level": 1,
    }
    try:
        _db().table(table).insert(payload).execute()
        return {"seeded": True, "payload": payload}
    except Exception as exc:
        return {"seeded": False, "reason": f"insert failed: {exc}"}


def main() -> None:
    checks = [
        ("table", "instructor_skill", None),
        ("table", "student_skill", None),
        ("table", "lesson_enrollment", None),
        ("column", "invoice", "period_start"),
        ("column", "invoice", "period_end"),
        ("column", "invoice_line", "lesson_id"),
    ]

    print("DB Verification Results")
    print("=" * 72)
    for check_type, table, column in checks:
        if check_type == "table":
            ok, detail = _check_table_exists(table)
            status = "PASS" if ok else "FAIL"
            print(f"[{status}] table {table}")
            if not ok:
                print(f"       detail: {detail}")
        else:
            assert column is not None
            ok, detail = _check_column_exists(table, column)
            status = "PASS" if ok else "FAIL"
            print(f"[{status}] column {table}.{column}")
            if not ok:
                print(f"       detail: {detail}")

    print("\nSeed Checks")
    print("=" * 72)
    instructor_seed = _seed_instructor_skill_if_empty()
    if instructor_seed.get("seeded"):
        print(f"[SEEDED] instructor_skill -> {instructor_seed['payload']}")
    else:
        print(f"[SKIPPED] instructor_skill -> {instructor_seed.get('reason')}")

    student_seed = _seed_student_skill_if_empty()
    if student_seed.get("seeded"):
        print(f"[SEEDED] student_skill -> {student_seed['payload']}")
    else:
        print(f"[SKIPPED] student_skill -> {student_seed.get('reason')}")


if __name__ == "__main__":
    main()
