from backend.app.singletons.database import DatabaseConnection


class Lesson:
    def __init__(self, lesson_id, student_id, instructor_id, room_id,
                 start_time, end_time, rate=None, status=None):
        self.lesson_id = lesson_id
        self.student_id = student_id
        self.instructor_id = instructor_id
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time
        self.rate = rate
        self.status = status

    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("lesson").select("*").execute().data

    @staticmethod
    def get(lesson_id):
        return (
            DatabaseConnection().client
            .table("lesson")
            .select("*")
            .eq("lesson_id", lesson_id)
            .execute()
            .data
        )

    @staticmethod
    def get_for_week(start, end):
        return (
            DatabaseConnection().client
            .table("lesson")
            .select("*")
            .gte("start_time", start)
            .lte("end_time", end)
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("lesson").insert(data).execute().data

    @staticmethod
    def update(lesson_id, data):
        return (
            DatabaseConnection().client
            .table("lesson")
            .update(data)
            .eq("lesson_id", lesson_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(lesson_id):
        return (
            DatabaseConnection().client
            .table("lesson")
            .delete()
            .eq("lesson_id", lesson_id)
            .execute()
            .data
        )
