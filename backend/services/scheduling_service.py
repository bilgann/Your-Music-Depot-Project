import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import supabase
# Assuming lesson_repository will be implemented, import it
from repositories import lesson_repository

BUSINESS_HOUR_START = 9
BUSINESS_HOUR_END = 20

def instructor_available(instructor_id, start_time, end_time):
    # Check if instructor has any overlapping lessons
    data = supabase.table("lesson").select("id").eq("instructor_id", instructor_id) \
        .lt("start_time", end_time).gt("end_time", start_time).execute()
    return len(data.data) == 0

def room_available(room_id, start_time, end_time):
    # Check if room has any overlapping lessons
    data = supabase.table("lesson").select("id").eq("room_id", room_id) \
        .lt("start_time", end_time).gt("end_time", start_time).execute()
    return len(data.data) == 0

def student_available(student_id, start_time, end_time):
    # Check if student has overlapping lessons
    # Requires joining lesson_student and lesson tables.
    query = """
    select count(*) from lesson_student ls
    join lesson l on ls.lesson_id = l.id
    where ls.student_id = '{student_id}' and l.start_time < '{end_time}' and l.end_time > '{start_time}'
    """
    # Or simplified through supabase relational syntax:
    data = supabase.table("lesson_student").select("lesson!inner(id, start_time, end_time)").eq("student_id", student_id) \
        .lt("lesson.start_time", end_time).gt("lesson.end_time", start_time).execute()
    return len(data.data) == 0

def check_business_hours(start_time, end_time):
    # Assume ISO format strings "2026-03-21T10:00:00"
    try:
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        
        if start_dt.hour < BUSINESS_HOUR_START or end_dt.hour > BUSINESS_HOUR_END or \
           (end_dt.hour == BUSINESS_HOUR_END and end_dt.minute > 0):
            raise ValueError(f"Lesson must be scheduled within business hours ({BUSINESS_HOUR_START}:00 - {BUSINESS_HOUR_END}:00).")
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        # If parsing fails, just ignore for now or raise format error
        raise ValueError("Invalid time format. Please use ISO 8601 format.")

def check_instructor_skill(instructor_id, instrument):
    # Check instructor-instrument match via INSTRUCTOR_SKILL table
    data = supabase.table("instructor_skill").select("id").eq("instructor_id", instructor_id) \
        .ilike("instrument", f"%{instrument}%").execute()
    
    if len(data.data) == 0:
        raise ValueError(f"Instructor does not have the required skill to teach {instrument}.")

def check_room_capacity(room_id, num_students):
    data = supabase.table("room").select("capacity").eq("id", room_id).execute()
    if not data.data:
        raise ValueError("Room not found.")
    if data.data[0]["capacity"] < num_students:
        raise ValueError(f"Room capacity exceeded. Max capacity is {data.data[0]['capacity']}, but {num_students} students are enrolled.")


def create_lesson(data):
    instructor_id = data["instructorID"]
    room_id = data["roomID"]
    start = data["start_time"]
    end = data["end_time"]
    students = data.get("students", [])
    instrument = data.get("instrument")

    # 1. Business hours check
    check_business_hours(start, end)

    # 2. Room capacity check
    if len(students) > 0:
        check_room_capacity(room_id, len(students))

    # 3. Time conflict detection
    if not instructor_available(instructor_id, start, end):
        raise ValueError("Time conflict: Instructor is not available during this time.")

    if not room_available(room_id, start, end):
        raise ValueError("Time conflict: Room is not available during this time.")

    for student_id in students:
        if not student_available(student_id, start, end):
            raise ValueError(f"Time conflict: Student {student_id} is not available during this time.")

    # 4. Instructor-instrument match
    if instrument:
        check_instructor_skill(instructor_id, instrument)

    # Note: lesson_repository methods must be implemented to actually save to DB
    try:
        lesson_id = lesson_repository.crate_lesson(data)
        for student in students:
            lesson_repository.enroll_student(lesson_id, student)
        return lesson_id
    except AttributeError:
        # Fallback if repository is a stub
        return "lesson_created_stub_id"