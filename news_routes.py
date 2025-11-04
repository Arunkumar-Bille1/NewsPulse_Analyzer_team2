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
