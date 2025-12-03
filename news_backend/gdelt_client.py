# news_backend/gdelt_client.py

import requests

BASE = "https://api.gdeltproject.org/api/v2/doc/doc"

ISO2_TO_COUNTRY = {
    "IN": "India",
    "US": "United States",
    "GB": "United Kingdom",
    "CA": "Canada",
    "AU": "Australia",
    "DE": "Germany",
    "FR": "France",
    "BR": "Brazil",
    "JP": "Japan",
    "CN": "China",
    "RU": "Russia",
    "ZA": "South Africa",
}


def fetch_docs(hours: int = 24, query: str = "india", max_records: int = 150):
    """
    Call GDELT DOC 2.0 and return a normalized list of article dicts
    with fields used by gdelt_ingest.py.
    """
    params = {
        "format": "JSON",
        "timespan": f"{hours}h",
        "maxrecords": max_records,
        "mode": "ArtList",
        "sort": "DateDesc",
        "query": query or "india",
    }

    r = requests.get(
        BASE,
        params=params,
        headers={"User-Agent": "newspulse/1.0"},
        timeout=30,
    )
    print("GDELT URL:", r.url, "HTTP", r.status_code)

    if r.status_code != 200:
        print("Body:", r.text[:200])
        return []

    try:
        data = r.json()
    except Exception:
        print("Non-JSON body:", r.text[:200])
        return []

    arts = data.get("articles") or data.get("artList") or []
    results = []

    for a in arts:
        url = (a.get("url") or "").strip()
        if not url:
            continue

        country_iso = (a.get("sourcecountry") or "").upper()
        country_name = ISO2_TO_COUNTRY.get(country_iso) or country_iso or None

        results.append(
            {
                "url": url,
                "title": a.get("title") or "",
                "description": a.get("seendescription") or a.get("description") or "",
                "content": a.get("body") or "",
                "source": a.get("source") or a.get("domain") or "",
                "published_at": a.get("seendate") or a.get("pubdate") or "",
                "image": a.get("image") or "",
                "keywords": a.get("themes") or [],
                "location": country_name,
                "country": country_name,
                "state": None,
                "city": None,
                # GDELT sometimes has geolocation fields; if not, leave None
                "lat": a.get("lat") or a.get("glat"),
                "lon": a.get("lon") or a.get("glon"),
            }
        )

    return results