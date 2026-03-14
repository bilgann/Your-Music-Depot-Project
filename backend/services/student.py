import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import supabase

def get_all_students():
    return supabase.table("student").select("*").execute().data

def get_student_by_id(student_id):
    return supabase.table("student").select("*").eq("student_id", student_id).execute().data

def create_student(data):
    return supabase.table("student").insert(data).execute().data

def update_student(student_id, data):
    return supabase.table("student").update(data).eq("student_id", student_id).execute().data

def delete_student(student_id):
    return supabase.table("student").delete().eq("student_id", student_id).execute().data