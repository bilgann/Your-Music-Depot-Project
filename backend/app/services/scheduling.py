from backend.app.exceptions.scheduling import InstructorUnavailableError, RoomUnavailableError
from backend.app.models.lesson import Lesson
from backend.app.models.scheduling import Schedule


def create_lesson(data):
    instructor_id = data["instructor_id"]
    room_id = data["room_id"]
    start = data["start_time"]
    end = data["end_time"]

    if not Schedule.instructor_available(instructor_id, start, end):
        raise InstructorUnavailableError("Instructor is not available during this time.")

    if not Schedule.room_available(room_id, start, end):
        raise RoomUnavailableError("Room is not available during this time.")

    return Lesson.create(data)
