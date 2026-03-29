# this is where the core scheduling logic will be implemented.
# This will include functions to create, update, and delete lessons, as well as any necessary validation and conflict checking.
from backend.app.exceptions.scheduling import InstructorUnavailableError, RoomUnavailableError


def create_lesson(data):

    instructor_id = data["instructorID"]
    room_id = data["roomID"]
    start = data["start_time"]
    end = data["end_time"]

    if not instructor_available(instructor_id, start, end):
        raise InstructorUnavailableError("Instructor is not available during this time.")

    if not room_available(room_id, start, end):
        raise RoomUnavailableError("Room is not available during this time.")

    lesson_id = lesson_repository.crate_lesson(data)

    for student in data["students"]:
        lesson_repository.enroll_student(lesson_id, student)

    return lesson_id
