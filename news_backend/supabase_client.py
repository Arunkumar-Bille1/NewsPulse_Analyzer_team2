import os
import json
from pprint import pprint
from supabase import create_client
from dotenv import load_dotenv

# ✅ Load environment variables (works even if .env is one level above)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(ENV_PATH)

# ✅ Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("SUPABASE_URL:", SUPABASE_URL or "❌ MISSING")
print("SUPABASE_KEY:", (SUPABASE_SERVICE_ROLE_KEY or "MISSING")[:6], "...")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Supabase URL or Service Role Key missing. Check your .env file.")

# ✅ Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# ==============================================================
# 📰  FETCH FUNCTIONS
# ==============================================================

def get_articles_by_category(category: str):
    """Fetch all articles by category"""
    response = supabase.table("articles").select("*").eq("category", category).execute()
    if getattr(response, "error", None):
        raise Exception(response.error.message)
    return response.data or []


def get_all_news():
    """Fetch all items from 'news' table"""
    response = supabase.table("news").select("*").execute()
    if response.status_code != 200:
        raise Exception(f"Failed to fetch news: {response.message}")
    return response.data or []


def get_all_articles():
    """Fetch all articles from Supabase"""
    response = supabase.table("articles").select("*").execute()
    if response.status_code != 200:
        raise Exception(f"Fetch failed: {response.status_code} {response.message}")
    return response.data or []


def fetch_all_articles(page_size: int = 1000, order_desc: bool = True):
    """
    Fetch all rows from 'articles' table in paginated chunks.
    Useful for large datasets.
    """
    start = 0
    all_rows = []
    order_kw = {"desc": order_desc}

    while True:
        query = (
            supabase.table("articles")
            .select("*")
            .order("published_at", **order_kw)
        )
        resp = query.range(start, start + page_size - 1).execute()
        batch = resp.data or []
        all_rows.extend(batch)

        if len(batch) < page_size:
            break
        start += page_size

    return all_rows


def fetch_articles_batch(offset: int, limit: int = 500):
    """Fetch a batch of articles for processing"""
    resp = (
        supabase.table("articles")
        .select("id,title,description,content")
        .order("id", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return resp.data or []


# ==============================================================
# 💾  UPSERT / UPDATE FUNCTIONS
# ==============================================================

def save_news_to_supabase(articles):
    """
    Insert or update articles in Supabase.
    Uses `url` as conflict key (must be UNIQUE in Supabase).
    """

    if not articles:
        print("[save_news_to_supabase] ⚠️ No articles to save.")
        return

    rows = []
    for a in articles:
        if not isinstance(a, dict):
            continue

        row = {
            "title": a.get("title") or "",
            "description": a.get("description") or "",
            "content": a.get("content") or "",
            "source": a.get("source", {}).get("name") if isinstance(a.get("source"), dict)
                       else (a.get("source") or ""),
            "published_at": a.get("published_at") or a.get("publishedAt") or None,
            "url": (a.get("url") or "").strip(),
            "image": a.get("image") or a.get("urlToImage") or "",
            "keywords": a.get("keywords") if a.get("keywords") is not None else [],
        }

        # ✅ Only include rows that have a valid URL (required for on_conflict)
        if row["url"]:
            rows.append(row)

    print(f"[save_news_to_supabase] Preparing to upsert {len(rows)} rows")

    if not rows:
        print("[save_news_to_supabase] ❌ No valid rows with URLs — skipping.")
        return

    try:
        resp = supabase.table("articles").upsert(rows, on_conflict="url").execute()
        if getattr(resp, "error", None):
            print("[save_news_to_supabase] ❌ Supabase error:", resp.error)
            raise Exception(resp.error)

        print(f"[save_news_to_supabase] ✅ Upsert success — {len(resp.data or [])} rows processed.")
    except Exception as e:
        print("[save_news_to_supabase] ❌ Exception during upsert:", str(e))
        print("🧾 Payload sample:", json.dumps(rows[:2], indent=2))
        raise


def update_article_keywords(rows: list[dict]):
    """Update keywords for existing articles"""
    if not rows:
        print("[update_article_keywords] ⚠️ No rows to update.")
        return

    for r in rows:
        if not ("id" in r and "keywords" in r):
            continue
        supabase.table("articles").update({"keywords": r["keywords"]}).eq("id", r["id"]).execute()
    print(f"[update_article_keywords] ✅ Updated keywords for {len(rows)} rows.")


# ==============================================================
# 🧪  LOCAL TEST
# ==============================================================

if __name__ == "__main__":
    print("\n[TEST] Running Supabase client test...")

    test_articles = [{
        "title": "AI transforming news analytics",
        "description": "Testing upsert pipeline",
        "content": "This is a test content item for TrendVista",
        "source": {"name": "TrendVista"},
        "publishedAt": "2025-11-08T10:00:00Z",
        "url": "https://example.com/test-article-001",
        "image": "https://example.com/test-image.jpg",
        "keywords": ["AI", "news", "test"]
    }]

    save_news_to_supabase(test_articles)
