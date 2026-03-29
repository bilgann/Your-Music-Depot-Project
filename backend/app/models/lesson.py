from backend.app.singletons.database import DatabaseConnection


def _db():
    """Helper to get the Supabase client from DatabaseConnection singleton."""
    return DatabaseConnection().client

class Lesson:
    def __init__(self, lesson_id, instructor_id, room_id, start, end):
        self.lesson_id = lesson_id
        self.instructor_id = instructor_id
        self.room_id = room_id
        self.start = start
        self.end = end

    # Repo Statics
    @staticmethod
    def get(lesson_id):
        response = _db().table("lesson").select("*").eq("lessonID", lesson_id).single().execute()
        return response.data

    @staticmethod
    def get_all():
        response = _db().table("lesson").select("*").execute()
        return response.data

    @staticmethod
    def get_by_week(start_date, end_date):
        response = _db().table("lesson").select("*").gte("date", start_date).lte("date", end_date).execute()
        return response.data

    @staticmethod
    def create(data):
        response = _db().table("lesson").insert(data).execute()
        return response.data

    @staticmethod
    def update(lesson_id, data):
        response = _db().table("lesson").update(data).eq("lessonID", lesson_id).execute()
        return response.data

    @staticmethod
    def delete(lesson_id):
        response = _db().table("lesson").delete().eq("lessonID", lesson_id).execute()
        return response.data
