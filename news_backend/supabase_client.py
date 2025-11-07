from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


print("URL:", SUPABASE_URL)
print("KEY:", (SUPABASE_SERVICE_ROLE_KEY or "MISSING")[:6], "...")



supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)



def get_articles_by_category(category: str):
    response = supabase.table("articles").select("*").eq("category", category).execute()
    if response.error:
        raise Exception(response.error.message)
    return response.data


def save_news_to_supabase(articles):
    rows = [{
        "title": a.get("title") or "",
        "description": a.get("description") or "",
        "content": a.get("content") or "",
        "source": a.get("source", {}).get("name") if isinstance(a.get("source"), dict) else (a.get("source") or ""),
        "published_at": a.get("published_at") or a.get("publishedAt") or None,
        "url": (a.get("url") or "").strip(),
        "image": a.get("image") or "",
        "keywords": a.get("keywords") if a.get("keywords") is not None else []
    } for a in articles]

    print(f"[upsert] payload_count={len(rows)}")
    resp = supabase.table("articles").upsert(rows, on_conflict="url").execute()
    if getattr(resp, "error", None):
        print("[upsert] error:", resp.error)
        raise Exception(str(resp.error))
    print(f"[upsert] returned_rows={len(resp.data or [])}")


def get_all_news():
    response = supabase.table("news").select("*").execute()
    if response.status_code != 200:
        raise Exception(f"Failed to fetch news: {response.message}")
    return response.data

def get_all_articles():
    response = supabase.table("articles").select("*").execute()
    if response.status_code != 200:
        raise Exception(f"Fetch failed: {response.status_code} {response.message}")
    return response.data


# existing imports & client creation here...

def fetch_all_articles(page_size: int = 1000, order_desc: bool = True):
    """
    Fetch all rows from articles table using paginated range() calls.
    Returns a Python list of article dicts.
    """
    start = 0
    all_rows: list[dict] = []
    order_kw = {"desc": order_desc}

    while True:
        q = supabase.table("articles").select("*").order("published_at", **order_kw)
        resp = q.range(start, start + page_size - 1).execute()
        batch = resp.data or []
        all_rows.extend(batch)
        if len(batch) < page_size:
            break
        start += page_size
    return all_rows


# news_backend/supabase_client.py
def fetch_articles_batch(offset: int, limit: int = 500):
    resp = (supabase.table("articles")
            .select("id,title,description,content")
            .order("id", desc=True)
            .range(offset, offset + limit - 1)
            .execute())
    return resp.data or []

def update_article_keywords(rows: list[dict]):
    if not rows:
        return
    # Use partial updates per id
    for r in rows:
        supabase.table("articles").update({"keywords": r["keywords"]}).eq("id", r["id"]).execute()
