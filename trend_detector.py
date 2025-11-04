import pandas as pd
import nltk
from nltk.corpus import stopwords
from sqlalchemy.orm import Session
from news_backend.database import SessionLocal
from news_backend.models import NewsBase
from collections import Counter
import re
from datetime import datetime, timedelta

from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def detect_trends_from_db():
    db: Session = SessionLocal()
    articles = db.query(NewsBase).all()
    db.close()

    if not articles:
        return {"topics": {}, "trending_keywords": []}

    # Combine title and description (could update to include more fields)
    news_data = pd.DataFrame({
        "title": [a.title or "" for a in articles],
        "date": [str(a.publishedAt.date()) if a.publishedAt else "2025-10-01" for a in articles]
    })

    # Step 1: Text Cleaning
    def preprocess(text):
        text = re.sub(r'\W+', ' ', text.lower())
        tokens = [word for word in text.split() if word not in stop_words]
        return ' '.join(tokens)

    news_data["cleaned"] = news_data["title"].apply(preprocess)

    # Step 2: Topic Modeling with BERTopic
    docs = news_data["cleaned"].tolist()
    vectorizer = CountVectorizer(ngram_range=(1, 2), stop_words='english')
    topic_model = BERTopic(vectorizer_model=vectorizer, language='english')
    topics, probs = topic_model.fit_transform(docs)
    topic_info = topic_model.get_topic_info()

    # Step 3: Format Topic Output
    topic_clusters = {}
    for _, row in topic_info.iterrows():
        topic_id = row["Topic"]
        keywords = row["Name"].split(", ")
        topic_clusters[f"Topic {topic_id}"] = keywords

    # Step 4: Frequency-based Trend Detection
    trending_words = Counter(" ".join(news_data["cleaned"]).split())
    top_trends = trending_words.most_common(10)
    trending_keywords_display = [
        {"word": word, "frequency": freq}
        for word, freq in top_trends
    ]

    return {
        "topics": topic_clusters,
        "trending_keywords": trending_keywords_display
    }



def get_topic_time_series(articles):
    """
        Analyze the frequency of each topic over time from a list of articles.
        Returns a pivoted time series table of topic frequency per date.

        Input:
            articles: List of dicts, each with 'publishedAt' (date string, e.g. '2025-10-28')
                      and 'topic_id' (cluster assigned by BERTopic, should skip '-1' outliers)

        Output:
            time_series: pandas DataFrame with dates as index, topics as columns, counts as values
        """
    now = datetime.now()
    five_minutes_ago = now - timedelta(minutes=5)
    # Build dataframe from articles, filtering out outliers
    df = pd.DataFrame([
        {'date': str(a['publishedAt'])[:16], 'topic': a['topic_id']}
        for a in articles
        if a['topic_id'] != "-1" and pd.to_datetime(a['publishedAt']) >= five_minutes_ago
    ])
    if df.empty:
        return []
    # Group by date and topic, count occurrences
    trends = df.groupby(['date', 'topic']).size().reset_index(name='count')
    # Pivot for charting: dates as rows, topics as columns
    pivot = trends.pivot(index='date', columns='topic', values='count').fillna(0).astype(int)
    # Optional: reset index for easy conversion to dict
    return pivot.reset_index().to_dict(orient="records")
