from keybert import KeyBERT
from sqlalchemy.orm import Session
from news_backend.database import SessionLocal
from news_backend.models import NewsBase

kw_model = KeyBERT()

def extract_keywords_for_articles(db: Session, top_n: int = 5):
    """
    Extract keywords for each news article and attach them.
    """
    articles = db.query(NewsBase).all()
    if not articles:
        return []

    results = []
    for article in articles:
        text = f"{article.title or ''} {article.description or ''}".strip()
        if not text:
            continue

        keywords = kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            top_n=top_n
        )
        # Just extract keyword strings
        keyword_list = [kw[0] for kw in keywords]

        # Attach keywords to the article object temporarily
        results.append({
            "id": article.id,
            "title": article.title,
            "description": article.description,
            "source": article.source,
            "publishedAt": article.publishedAt,
            "url": article.url,
            "image": article.image,
            "keywords": keyword_list
        })

    return results
