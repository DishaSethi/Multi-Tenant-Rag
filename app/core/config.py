import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
    SUPABASE_URL=os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    SUPABASE_SERVICE_KEY = SUPABASE_KEY


settings=Settings()