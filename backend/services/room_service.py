import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import supabase

def get_all_rooms():
    return supabase.table("room").select("*").execute().data

def get_room_by_id(room_id):
    return supabase.table("room").select("*").eq("room_id", room_id).execute().data

def create_room(data):
    return supabase.table("room").insert(data).execute().data

def update_room(room_id, data):
    return supabase.table("room").update(data).eq("room_id", room_id).execute().data

def delete_room(room_id):
    return supabase.table("room").delete().eq("room_id", room_id).execute().data