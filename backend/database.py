import os 
from supabase import create_client
from dotenv import load_dotenv

# load environment variables from .env file (next to this module)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in the environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)