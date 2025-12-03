import os
import json
from pprint import pprint
from supabase import create_client
from dotenv import load_dotenv

# Load env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("SUPABASE_URL:", SUPABASE_URL or "❌ MISSING")
print("SUPABASE_KEY:", (SUPABASE_SERVICE_ROLE_KEY or "MISSING")[:6], "...")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Supabase credentials missing. Check .env.")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ==============================================================
#  FETCH FUNCTIONS
# ==============================================================

def get_articles_by_category(category: str):
    response = supabase.table("articles").select("*").eq("category", category).execute()
    if getattr(response, "error", None):
        raise Exception(response.error.message)
    return response.data or []


def get_all_news():
    response = supabase.table("news").select("*").execute()
    if response.status_code != 200:
        raise Exception(f"Failed to fetch news: {response.message}")
    return response.data or []


def get_all_articles():
    response = supabase.table("articles").select("*").execute()
    if response.status_code != 200:
        raise Exception(f"Fetch failed: {response.status_code} {response.message}")
    return response.data or []


def fetch_all_articles(page_size: int = 1000, order_desc: bool = True):
    start = 0
    all_rows = []
    order_kw = {"desc": order_desc}

    while True:
        query = (
            supabase.table("articles")
            .select("*")
            .order("published_at", **order_kw)
        )

        # simple retry around the HTTP call
        last_err = None
        for attempt in range(3):
            try:
                resp = query.range(start, start + page_size - 1).execute()
                break
            except Exception as e:
                last_err = e
                print(f"[fetch_all_articles] attempt {attempt+1} failed: {e}")
        else:
            # after 3 failed attempts, stop to avoid 500 on frontend
            print("[fetch_all_articles] giving up after 3 attempts")
            break

        batch = resp.data or []
        all_rows.extend(batch)

        if len(batch) < page_size:
            break

        start += page_size

    return all_rows


def fetch_articles_batch(offset: int, limit: int = 500):
    resp = (
        supabase.table("articles")
        .select("id,title,description,content")
        .order("id", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return resp.data or []

# ==============================================================
# UPSERT / UPDATE FUNCTIONS
# ==============================================================

def save_news_to_supabase(articles):
    """
    Insert or update articles into Supabase.
    Removes duplicate URLs before UPSERT to avoid conflict errors.
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
            "source": a.get("source", {}).get("name")
            if isinstance(a.get("source"), dict)
            else (a.get("source") or ""),
            "published_at": a.get("published_at") or a.get("publishedAt") or None,
            "url": (a.get("url") or "").strip(),
            "image": a.get("image") or a.get("urlToImage") or "",
            "keywords": a.get("keywords") if a.get("keywords") is not None else [],
            # ✅ geo fields (from GDELT or tagger)
            "location": a.get("location"),
            "lat": a.get("lat"),
            "lon": a.get("lon"),
            "country": a.get("country"),
            "state": a.get("state"),
            "city": a.get("city"),
        }

        if row["url"]:
            rows.append(row)

    print(f"[save_news_to_supabase] Raw rows: {len(rows)}")

    # -------- REMOVE DUPLICATE URLS --------
    unique_map = {}
    duplicates = []

    for r in rows:
        url = r["url"]
        if url in unique_map:
            duplicates.append(url)
        unique_map[url] = r

    if duplicates:
        print(f"[save_news_to_supabase] ⚠️ Duplicate URLs removed: {len(set(duplicates))}")
        print("Sample duplicates:", list(set(duplicates))[:5])

    clean_rows = list(unique_map.values())

    print(f"[save_news_to_supabase] Final rows (unique): {len(clean_rows)}")

    if not clean_rows:
        print("[save_news_to_supabase] ❌ No valid rows after cleaning.")
        return

    # -------- UPSERT CLEAN LIST --------
    try:
        resp = supabase.table("articles").upsert(
            clean_rows,
            on_conflict="url"
        ).execute()

        if getattr(resp, "error", None):
            raise Exception(resp.error)

        print(f"[save_news_to_supabase] ✅ Upsert success — {len(resp.data or [])} rows processed.")

    except Exception as e:
        print("[save_news_to_supabase] ❌ Exception:", str(e))
        print("Payload example:", json.dumps(clean_rows[:2], indent=2))
        raise


def update_article_keywords(rows: list[dict]):
    """Update keywords for existing records."""
    if not rows:
        print("[update_article_keywords] ⚠️ No rows provided.")
        return

    updated = 0
    for r in rows:
        if "id" in r and "keywords" in r:
            supabase.table("articles").update(
                {"keywords": r["keywords"]}
            ).eq("id", r["id"]).execute()
            updated += 1

    print(f"[update_article_keywords] ✅ Updated {updated} rows.")

# ==============================================================
# GEO FUNCTIONS
# ==============================================================

def get_articles(country=None, state=None, city=None):
    try:
        query = supabase.table("articles").select(
            "id, url, title, description, country, state, city, lat, lon, location"
        )
        if country:
            query = query.eq("country", country)
        if state:
            query = query.eq("state", state)
        if city:
            query = query.eq("city", city)

        resp = query.execute()
        return resp.data or []

    except Exception as e:
        print("[get_articles] ❌ Error:", str(e))
        return []


def save_geo_tag(article_url: str, country: str, state: str = "",
                 city: str = "", lat: float = None, lon: float = None, location: str = None):
    try:
        update_data = {
            "country": country,
            "state": state,
            "city": city,
            "lat": lat,
            "lon": lon,
            "location": location,
        }
        clean = {k: v for k, v in update_data.items() if v is not None}

        resp = supabase.table("articles").update(clean).eq("url", article_url).execute()

        if getattr(resp, "error", None):
            raise Exception(resp.error)

        return resp.data or []

    except Exception as e:
        print("[save_geo_tag] ❌ Error:", str(e))
        raise


def get_geo_analytics():
    try:
        resp = supabase.rpc("get_geo_summary").execute()
        if not getattr(resp, "error", None):
            return resp.data

        rows = (
            supabase.table("articles")
            .select("country, lat, lon")
            .not_.is_("lat", None)
            .not_.is_("lon", None)
            .execute()
        ).data or []

        grouped = {}
        for r in rows:
            c = r.get("country") or "Unknown"
            if c not in grouped:
                grouped[c] = {"count": 0, "locations": []}

            grouped[c]["count"] += 1
            grouped[c]["locations"].append({"lat": r["lat"], "lon": r["lon"]})

        return grouped

    except Exception as e:
        print("[get_geo_analytics] ❌ Error:", str(e))
        return {}


def fetch_articles_batch(offset: int = 0, limit: int = 200):
    try:
        resp = (
            supabase.table("articles")
            .select("id, url, title, description, content, country, state, city, lat, lon")
            .order("id", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return resp.data or []

    except Exception as e:
        print("[fetch_articles_batch] ❌ Error:", str(e))
        return []
