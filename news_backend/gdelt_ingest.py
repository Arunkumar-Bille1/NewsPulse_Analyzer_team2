# news_backend/gdelt_ingest.py

from datetime import datetime
from dateutil import parser as dtparser
from typing import List, Dict, Any

from .gdelt_client import fetch_docs   # copy your existing gdelt_client.py into news_backend
from .supabase_client import save_news_to_supabase


def parse_gdelt_datetime(s: str | None):
    if not s:
        return None
    s = s.strip()
    try:
        return dtparser.parse(s)
    except Exception:
        return None


def fetch_gdelt_and_upsert(
    hours: int = 24,
    query: str | None = "(AI OR climate OR india)",
    max_records: int = 150,
) -> int:
    """
    Pull articles from GDELT DOC 2.0 and upsert them into Supabase 'articles'
    with geo fields (location, lat, lon) taken directly from the payload.
    """
    docs: List[Dict[str, Any]] = fetch_docs(
        hours=hours,
        query=query or "india",
        max_records=max_records,
    )

    if not docs:
        print("[GDELT] No documents returned.")
        return 0

    rows: List[Dict[str, Any]] = []

    for d in docs:
        url = (d.get("url") or "").strip()
        if not url:
            continue

        published_raw = d.get("published_at")
        published = parse_gdelt_datetime(published_raw) or datetime.utcnow()

        row = {
            "title": d.get("title") or "(untitled)",
            "description": d.get("description") or "",
            "content": d.get("content") or "",
            "source": d.get("source") or "",
            "published_at": published.isoformat(),
            "url": url,
            "image": d.get("image") or "",
            "keywords": d.get("keywords") or [],
            # geo from GDELT (or mapped country name)
            "location": d.get("location"),
            "lat": d.get("lat"),
            "lon": d.get("lon"),
            "country": d.get("country") or d.get("location"),
            "state": d.get("state"),
            "city": d.get("city"),
        }
        rows.append(row)

    print(f"[GDELT] Prepared {len(rows)} rows for Supabase upsert.")
    if rows:
        save_news_to_supabase(rows)
    return len(rows)


if __name__ == "__main__":
    fetch_gdelt_and_upsert(hours=168, query="(AI OR climate OR india)", max_records=150)