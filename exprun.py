from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env from current directory

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("URL:", SUPABASE_URL)
print("KEY:", SUPABASE_KEY[:6], "...")  # For checking first letters, don't print full key

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

test_row = [{
    "title": "Test Title",
    "description": "Test Description",
    "source": "Test Source",
    "publishedAt": "2025-11-05T12:00:00Z",
    "url": "https://test.com/news/1",
    "image": "",
    "keywords": ["test", "news", "demo"]
}]

response = supabase.table("news").insert(test_row).execute()

print("Data:", response.data)
print("Status code:", response.status_code)
print("Message:", getattr(response, "message", None))

