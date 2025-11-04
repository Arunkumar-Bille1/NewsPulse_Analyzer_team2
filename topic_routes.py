# news_backend/routers/topic_routes.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from news_backend.database import get_db
from news_backend.models import NewsBase
from news_backend.topic_modeler import train_topic_model, summarize_topics, get_topic_info

router = APIRouter(prefix="/topics", tags=["Topic Modeling"])

@router.post("/train")
def train_topics(db: Session = Depends(get_db)):
    """
    Train BERTopic model on all news articles from the database.
    """
    articles = db.query(NewsBase).all()
    if not articles:
        raise HTTPException(status_code=404, detail="No news articles found to train topics.")

    docs = [article.title + " " + (article.description or "") for article in articles]
    train_topic_model(docs)
    return {"message": f"✅ Model trained successfully on {len(docs)} articles."}


@router.get("/summary")
def get_topic_summary(top_n: int = 5):
    """
    Get top N topics summary (topic_id, count, keywords).
    """
    try:
        summary = summarize_topics(top_n)
        return {"topics": summary}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/info")
def topic_info():
    """
    Get full topic info DataFrame (as JSON).
    """
    try:
        info_df = get_topic_info()
        return {"topic_info": info_df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
