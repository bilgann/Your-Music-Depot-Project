import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import supabase

def get_all_instructors():
    return supabase.table("instructor").select("*").execute().data

def get_instructor_by_id(instructor_id):
    return supabase.table("instructor").select("*").eq("instructor_id", instructor_id).execute().data

def create_instructor(data):
    return supabase.table("instructor").insert(data).execute().data

def update_instructor(instructor_id, data):
    return supabase.table("instructor").update(data).eq("instructor_id", instructor_id).execute().data

def delete_instructor(instructor_id):
    return supabase.table("instructor").delete().eq("instructor_id", instructor_id).execute().data