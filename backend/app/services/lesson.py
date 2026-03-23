# Handles database operations related to lessons.

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import supabase

def get_lessons_for_week(start, end):
    return supabase.table("lesson").select("*").gte("start_time", start).lte("end_time", end).execute().data