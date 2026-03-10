# defines data structure
class Lesson:
    def __init__(self, instructor_id, room_id, start, end):
        self.instructor_id = instructor_id
        self.room_id = room_id
        self.start = start
        self.end = end