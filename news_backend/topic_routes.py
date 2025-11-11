# news_backend/routers/topic_routes.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from news_backend.database import get_db
from news_backend.models import NewsBase, Topic
from news_backend.topic_modeler import train_topic_model, summarize_topics, get_topic_info

router = APIRouter(prefix="/topics", tags=["Topic Modeling"])


@router.post("/train")
def train_topics(db: Session = Depends(get_db)):
    """
    Train BERTopic model on all news articles from the database,
    and save topics to the 'topics' table.
    """
    articles = db.query(NewsBase).all()
    if not articles:
        raise HTTPException(status_code=404, detail="No news articles found to train topics.")

    # Combine title + description for modeling
    docs = [article.title + " " + (article.description or "") for article in articles]

    # Train the model and automatically save topics to DB (via topic_modeler)
    train_topic_model(docs)

    return {"message": f"✅ Model trained successfully on {len(docs)} articles."}


@router.get("/summary")
def get_topic_summary(db: Session = Depends(get_db), top_n: int = 5):
    """
    Get top N topics summary (topic_name, keywords, and size).
    If DB is empty, fallback to in-memory summarize_topics().
    """
    try:
        topics = db.query(Topic).order_by(Topic.size.desc()).limit(top_n).all()
        if topics:
            # return topics stored in database
            return {
                "topics": [
                    {
                        "id": t.id,
                        "topic_name": t.topic_name,
                        "keywords": t.keywords,
                        "size": t.size,
                        "created_at": t.created_at
                    }
                    for t in topics
                ]
            }
        else:
            # fallback to memory model summary
            summary = summarize_topics()
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



@router.get("/all")
def get_all_topics(db: Session = Depends(get_db)):
    """
    Get all topics from the database for frontend visualization.
    """
    topics = db.query(Topic).order_by(Topic.created_at.desc()).all()
    return [
        {
            "id": t.id,
            "topic_name": t.topic_name,
            "keywords": t.keywords,
            "representative_docs": t.representative_docs,
            "size": t.size,
            "created_at": t.created_at
        }
        for t in topics
    ]
