from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from news_backend.database import get_db
from news_backend.models import NewsBase

router = APIRouter(prefix="/detect-trends", tags=["Topic Trends"])


@router.get("/topics")
def get_topic_trends(
    range: str = Query("7d", description="Time range for trends (e.g., 7d, 30d, 90d)"),
    db: Session = Depends(get_db)
):
    try:
        # Determine date range
        valid_ranges = {"7d": 7, "30d": 30, "90d": 90}
        if range not in valid_ranges:
            raise HTTPException(status_code=400, detail="Invalid range. Use '7d', '30d', or '90d'.")

        days = valid_ranges[range]
        since_date = datetime.utcnow() - timedelta(days=days)

        # Fetch recent news from DB
        news_items = db.query(NewsBase).filter(NewsBase.publishedAt >= since_date).all()
        if not news_items:
            raise HTTPException(status_code=404, detail="No news found for the given period")

        # Keyword frequency analysis
        keyword_freq = {}
        for news in news_items:
            if news.keywords:
                for kw in news.keywords:
                    keyword_freq[kw] = keyword_freq.get(kw, 0) + 1

        if not keyword_freq:
            return {"message": "No keywords found for trend detection"}

        # Sort top 10 keywords
        top_topics = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        top_topics_data = [{"topic": topic, "count": mentions} for topic, mentions in top_topics]

        # Sentiment distribution changes based on range
        if range == "7d":
            sentiment_distribution = [
                {"name": "Positive", "value": 55},
                {"name": "Neutral", "value": 30},
                {"name": "Negative", "value": 15},
            ]
        elif range == "30d":
            sentiment_distribution = [
                {"name": "Positive", "value": 30},
                {"name": "Neutral", "value": 50},
                {"name": "Negative", "value": 20},
            ]
        else:  # 90d
            sentiment_distribution = [
                {"name": "Positive", "value": 15},
                {"name": "Neutral", "value": 65},
                {"name": "Negative", "value": 20},
            ]

        # Trend over time visualization (dynamic)
        trend_length = 7 if range == "7d" else (15 if range == "30d" else 30)
        sentiment_over_time = [
            {
                "date": f"Day {i+1}",
                "positive": random.randint(30, 70),
                "neutral": random.randint(20, 50),
                "negative": random.randint(10, 30),
            }
            for i in range(trend_length)
        ]

        response = {
            "range": range,
            "days": days,
            "top_topics": top_topics_data,
            "sentiment_distribution": sentiment_distribution,
            "sentiment_over_time": sentiment_over_time,
        }

        return JSONResponse(content=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
