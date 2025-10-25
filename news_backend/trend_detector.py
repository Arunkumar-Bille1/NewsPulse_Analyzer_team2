import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sqlalchemy.orm import Session
from news_backend.database import SessionLocal
from news_backend.models import NewsBase
from collections import Counter
import re

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def detect_trends_from_db():
    db: Session = SessionLocal()
    articles = db.query(NewsBase).all()
    db.close()

    if not articles:
        return {"topics": [], "trending_keywords": []}

    # Combine title and description
    news_data = pd.DataFrame({
        "title": [a.title or "" for a in articles],
        "date": [str(a.publishedAt.date()) if a.publishedAt else "2025-10-01" for a in articles]
    })

    # 🔹 Step 1: Text Cleaning
    def preprocess(text):
        text = re.sub(r'\W+', ' ', text.lower())
        tokens = [word for word in text.split() if word not in stop_words]
        return ' '.join(tokens)

    news_data["cleaned"] = news_data["title"].apply(preprocess)

    # 🔹 Step 2: Vectorize for Topic Modeling
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    X = vectorizer.fit_transform(news_data["cleaned"])

    # 🔹 Step 3: Topic Modeling with LDA (from sklearn)
    lda = LatentDirichletAllocation(n_components=3, random_state=42)
    lda.fit(X)

    feature_names = vectorizer.get_feature_names_out()
    topics = {}
    for idx, topic in enumerate(lda.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-6:-1]]
        topics[f"Topic {idx+1}"] = top_words

    # 🔹 Step 4: Frequency-based Trend Detection
    trending_words = Counter(" ".join(news_data["cleaned"]).split())
    top_trends = trending_words.most_common(10)

    # Return JSON response
    return {
        "topics": topics,
        "trending_keywords": [
            {"word": word, "frequency": freq} for word, freq in top_trends
        ]
    }
