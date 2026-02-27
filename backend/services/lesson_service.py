import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import supabase

def get_all_lessons():
    return supabase.table("lesson").select("*").execute().data

def get_lesson_by_id(lesson_id):
    return supabase.table("lesson").select("*").eq("lesson_id", lesson_id).execute().data

def create_lesson(data):
    return supabase.table("lesson").insert(data).execute().data

def update_lesson(lesson_id, data):
    return supabase.table("lesson").update(data).eq("lesson_id", lesson_id).execute().data

def delete_lesson(lesson_id):
    return supabase.table("lesson").delete().eq("lesson_id", lesson_id).execute().data