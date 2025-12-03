# news_backend/routers/news_routes.py

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from news_backend.database import get_db
from news_backend.models import NewsBase

router = APIRouter(prefix="/news", tags=["News Articles"])

@router.get("")
def get_articles(query: str = Query(None), db: Session = Depends(get_db)):
    """
    Fetch articles from the database.
    If 'query' is provided, filter by title or description.
    Example: /news?query=AI
    """
    if query:
        articles = db.query(NewsBase).filter(
            (NewsBase.title.ilike(f"%{query}%")) |
            (NewsBase.description.ilike(f"%{query}%"))
        ).all()
    else:
        articles = db.query(NewsBase).all()

    if not articles:
        raise HTTPException(status_code=404, detail="No articles found.")
    
    return articles
from fastapi import APIRouter, Query
from news_backend.news_fetcher import get_combined_news

router = APIRouter(prefix="/news", tags=["News"])

@router.get("/recent-articles")
def recent_articles(query: str = "technology"):
    articles = get_combined_news(query)
    return {"articles": articles}
# --- Keywords Route ---
from news_backend.keyword_extractor import extract_keywords_for_articles
from news_backend.database import get_db
from sqlalchemy.orm import Session

@router.get("/trending-keywords")
def get_trending_keywords(db: Session = Depends(get_db)):
    """
    Returns extracted keywords for all articles (top 5 each).
    Frontend uses this for Top Trending Keywords box.
    """
    keywords = extract_keywords_for_articles(db)
    return {"keywords": keywords}
@router.get("/trending")
def get_trending_news(db: Session = Depends(get_db)):
    """
    Returns latest 20 articles sorted by publishedAt.
    """
    articles = db.query(NewsBase).order_by(NewsBase.publishedAt.desc()).limit(20).all()
    return {"articles": articles}