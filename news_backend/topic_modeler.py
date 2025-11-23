from typing import List, Tuple, Any
from datetime import datetime
import json

from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from news_backend.database import SessionLocal
from news_backend.models import Topic, NewsBase

# Global BERTopic model
topic_model: BERTopic | None = None


def train_topic_model(docs: List[str]) -> Tuple[List[int], List[float]]:
    """
    Train BERTopic on provided documents and save results to DB.
    """
    global topic_model

    if not docs:
        return [], []

    vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words="english")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

    topic_model = BERTopic(
        embedding_model=embedding_model,
        vectorizer_model=vectorizer_model,
        language="english",
    )

    topics, probs = topic_model.fit_transform(docs)

    # Safely persist topics
    save_topics_to_db()

    return topics, probs


def get_topic_info() -> Any:
    if topic_model is None:
        raise ValueError("Model has not been trained yet.")
    return topic_model.get_topic_info()


def get_docs_for_topic(topic_id: int) -> Any:
    if topic_model is None:
        raise ValueError("Model has not been trained yet.")
    return topic_model.get_representative_docs().get(topic_id, [])


def summarize_topics() -> list:
    if topic_model is None:
        raise ValueError("Model has not been trained yet.")

    topic_info = topic_model.get_topic_info()
    summaries = []

    for _, row in topic_info.iterrows():
        topic_id = row["Topic"]
        keywords = row["Name"]
        summaries.append(f"Topic {topic_id}: {keywords}")

    return summaries


def save_topics_to_db() -> None:
    """
    Save BERTopic results into the 'topics' table safely.
    Converts lists/dicts into strings or JSON before insertion.
    """
    global topic_model

    # If training failed or model not fitted, just skip
    if topic_model is None:
        return

    try:
        topic_info = topic_model.get_topic_info()
        representative_docs = topic_model.get_representative_docs()
    except Exception:
        # Model not fitted yet or other internal error; do not crash the API
        return

    db: Session = SessionLocal()
    try:
        # Optional: clear old topics
        db.query(Topic).delete()

        for _, row in topic_info.iterrows():
            topic_id = row["Topic"]
            if topic_id == -1:  # skip outliers
                continue

            keywords = row.get("Representation")
            if isinstance(keywords, list):
                keywords = ", ".join(str(k) for k in keywords)
            else:
                keywords = str(keywords)

            docs = representative_docs.get(topic_id, [])
            try:
                docs_json = json.dumps(docs, ensure_ascii=False)
            except Exception:
                docs_json = json.dumps([str(d) for d in docs])

            topic = Topic(
                topic_name=row["Name"] if "Name" in row else f"Topic {topic_id}",
                keywords=keywords,
                representative_docs=docs_json,
                size=int(row["Count"]),
                created_at=datetime.utcnow(),
            )
            db.add(topic)

        db.commit()
        print("✅ Topics saved successfully to database.")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Error saving topics: {e}")
        # do not re-raise here; we don't want /news to 500 because of topics
    finally:
        db.close()


def detect_topics() -> list:
    """
    Fetches all articles, trains BERTopic model,
    and returns summarized topics.
    """
    db = SessionLocal()
    try:
        articles = db.query(NewsBase).all()
        docs = [
            f"{a.title or ''} {a.description or ''}".strip()
            for a in articles
            if (a.title or a.description)
        ]

        if not docs:
            return []

        train_topic_model(docs)
        return summarize_topics()
    finally:
        db.close()
