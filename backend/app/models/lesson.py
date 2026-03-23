import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.singletons.database import SupabaseClient

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
        response = supabase.table("lesson").select("*").eq("lessonID", lesson_id).single().execute()
        return response.data

    @staticmethod
    def get_all():
        response = supabase.table("lesson").select("*").execute()
        return response.data

    @staticmethod
    def get_by_week(start_date, end_date):
        response = supabase.table("lesson").select("*").gte("date", start_date).lte("date", end_date).execute()
        return response.data

    @staticmethod
    def create(data):
        response = supabase.table("lesson").insert(data).execute()
        return response.data

    @staticmethod
    def update(lesson_id, data):
        response = supabase.table("lesson").update(data).eq("lessonID", lesson_id).execute()
        return response.data

    @staticmethod
    def delete(lesson_id):
        response = supabase.table("lesson").delete().eq("lessonID", lesson_id).execute()
        return response.data
