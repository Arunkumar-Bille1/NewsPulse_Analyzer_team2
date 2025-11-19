import datetime
import requests
import re
from fastapi import APIRouter, Query, Depends
from textblob import TextBlob
from sqlalchemy.orm import Session

from news_backend.database import get_db
from news_backend.topic_modeler import detect_topics as ml_detect_topics


# ======================================================
# ROUTER (ONE TIME ONLY)
# ======================================================
router = APIRouter(prefix="/detect-trends", tags=["Trends"])


# ======================================================
# API KEYS
# ======================================================
NEWS_API_KEY = "fd6b4247f1054b2e8b2f3c1eed92ee45"
GNEWS_API_KEY = "2c36917d2300c1c6914eafe469e128e1"
REDDIT_CLIENT_ID = "up9mA01v608o84gLtvMhYA"
REDDIT_SECRET = "0z_wuVPMlo3o5_Si7IoxmRWOhF7iaA"


# ======================================================
# 1) SENTIMENT + CATEGORY TREND DETECTION
# ======================================================
@router.get("/topics")
def detect_trends_topics(time_range: str = Query("7d", alias="range")):

    # ---------- Range Setup ----------
    range_map = {"7d": 7, "30d": 30, "90d": 90}
    total_days = range_map.get(time_range, 7)

    end_date = datetime.datetime.utcnow().date()
    start_date = end_date - datetime.timedelta(days=total_days)

    # ---------- Topic Categories ----------
    topic_categories = {
        "Business": ["market", "stock", "finance", "trade", "economy", "company"],
        "Politics": ["government", "policy", "election", "minister", "law", "politics"],
        "Technology": ["ai", "tech", "software", "internet", "data", "robot", "innovation"],
        "Sports": ["match", "football", "cricket", "tournament", "goal", "player", "team"],
        "Entertainment": ["movie", "film", "music", "celebrity", "actor", "netflix", "show"],
        "Science": ["space", "nasa", "discovery", "research", "scientist", "experiment"],
        "Health": ["health", "vaccine", "virus", "doctor", "medical", "covid"],
        "Education": ["school", "college", "student", "education", "teacher", "university"],
    }

    topic_counts = {t: 0 for t in topic_categories}
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    sentiment_by_date = {}


    # ======================================================
    # FETCH FUNCTIONS
    # ======================================================
    def fetch_newsapi(from_d, to_d):
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q=technology OR politics OR sports OR business OR entertainment OR health&"
            f"from={from_d}&to={to_d}&language=en&pageSize=100&apiKey={NEWS_API_KEY}"
        )
        r = requests.get(url)
        if r.status_code != 200:
            print("NewsAPI Error:", r.text)
            return []
        return r.json().get("articles", [])


    def fetch_gnews(from_d, to_d):
        url = (
            f"https://gnews.io/api/v4/search?"
            f"q=technology OR politics OR sports OR business OR entertainment OR health&"
            f"from={from_d}&to={to_d}&lang=en&max=100&token={GNEWS_API_KEY}"
        )
        r = requests.get(url)
        if r.status_code != 200:
            print("GNews Error:", r.text)
            return []

        cleaned = []
        for a in r.json().get("articles", []):
            cleaned.append({
                "title": a.get("title"),
                "description": a.get("description"),
                "content": a.get("content"),
                "publishedAt": a.get("publishedAt")
            })
        return cleaned


    def fetch_reddit():
        auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_SECRET)
        data = {"grant_type": "client_credentials"}
        headers = {"User-Agent": "TrendDetector/1.0"}

        token_res = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth, data=data, headers=headers,
        )
        if token_res.status_code != 200:
            print("Reddit Auth Error:", token_res.text)
            return []

        token = token_res.json()["access_token"]
        headers["Authorization"] = f"bearer {token}"

        posts = []
        for sub in ["news", "worldnews"]:
            url = f"https://oauth.reddit.com/r/{sub}/hot?limit=50"
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                continue

            for item in res.json()["data"]["children"]:
                post = item["data"]
                posts.append({
                    "title": post.get("title"),
                    "description": post.get("selftext"),
                    "content": post.get("selftext"),
                    "publishedAt": post.get("created_utc")
                })

        return posts


    # ======================================================
    # COLLECT ALL ARTICLES
    # ======================================================
    all_articles = []

    remaining = total_days
    current = start_date

    while remaining > 0:
        chunk = min(30, remaining)
        chunk_end = current + datetime.timedelta(days=chunk)
        all_articles += fetch_newsapi(current.strftime("%Y-%m-%d"),
                                      chunk_end.strftime("%Y-%m-%d"))
        current = chunk_end
        remaining -= chunk

    all_articles += fetch_gnews(start_date, end_date)
    all_articles += fetch_reddit()

    # Deduplicate
    unique = {}
    for a in all_articles:
        t = (a.get("title") or "").lower().strip()
        if t not in unique:
            unique[t] = a
    all_articles = list(unique.values())

    if not all_articles:
        return {"message": "No articles found"}


    # ======================================================
    # ANALYZE ARTICLES
    # ======================================================
    for article in all_articles:
        raw_date = article.get("publishedAt")
        pub_date = None

        # ISO-format date (NewsAPI/GNews)
        if isinstance(raw_date, str):
            try:
                pub_date = datetime.datetime.fromisoformat(raw_date.replace("Z", "")).date()
            except:
                pass

        # Reddit timestamp
        if pub_date is None and isinstance(raw_date, (int, float)):
            pub_date = datetime.datetime.utcfromtimestamp(raw_date).date()

        if pub_date is None:
            continue

        pub_date = pub_date.strftime("%Y-%m-%d")

        # Build text
        text = " ".join([
            (article.get("title") or "").lower(),
            (article.get("description") or "").lower(),
            (article.get("content") or "").lower(),
        ])
        text = re.sub(r"[^a-z\s]", "", text)

        if not text:
            continue

        # Topic category detection
        for topic, keys in topic_categories.items():
            if any(k in text for k in keys):
                topic_counts[topic] += 1
                break

        # Sentiment
        polarity = TextBlob(text).sentiment.polarity
        sentiment = "positive" if polarity > 0.2 else "negative" if polarity < -0.2 else "neutral"
        sentiment_counts[sentiment] += 1

        if pub_date not in sentiment_by_date:
            sentiment_by_date[pub_date] = {"positive": 0, "neutral": 0, "negative": 0}
        sentiment_by_date[pub_date][sentiment] += 1


    # ======================================================
    # FILL DATE GAPS
    # ======================================================
    complete_trend = []
    cur = start_date

    while cur <= end_date:
        d = cur.strftime("%Y-%m-%d")
        vals = sentiment_by_date.get(d, {"positive": 0, "neutral": 0, "negative": 0})
        complete_trend.append({"date": d, **vals})
        cur += datetime.timedelta(days=1)

    # Weekly averages for 90 days
    if total_days == 90:
        weekly = []
        for i in range(0, len(complete_trend), 7):
            chunk = complete_trend[i:i+7]
            weekly.append({
                "date": chunk[-1]["date"],
                "positive": sum(c["positive"] for c in chunk),
                "neutral": sum(c["neutral"] for c in chunk),
                "negative": sum(c["negative"] for c in chunk)
            })
        complete_trend = weekly


    # ======================================================
    # RESPONSE
    # ======================================================
    top_topics = [{"topic": k, "count": v} for k, v in topic_counts.items()]
    top_topics.sort(key=lambda x: x["count"], reverse=True)

    return {
        "sources_used": ["NewsAPI", "GNews", "Reddit"],
        "from_date": start_date.strftime("%Y-%m-%d"),
        "to_date": end_date.strftime("%Y-%m-%d"),
        "article_count": len(all_articles),
        "top_topics": top_topics,
        "sentiment_distribution": [
            {"name": "Positive", "value": sentiment_counts["positive"]},
            {"name": "Neutral", "value": sentiment_counts["neutral"]},
            {"name": "Negative", "value": sentiment_counts["negative"]},
        ],
        "sentiment_over_time": complete_trend
    }



# ======================================================
# 2) ML-BASED TOPIC MODELING (BERTopic)
# ======================================================
@router.get("/ml-topics")
def get_ml_topics(db: Session = Depends(get_db)):
    """
    ML topics from BERTopic (separate from sentiment API)
    """
    topics = ml_detect_topics(db)
    return {"topics": topics}
