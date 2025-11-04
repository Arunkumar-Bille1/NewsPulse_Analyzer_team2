from bertopic import BERTopic
from typing import List, Tuple, Any
from sklearn.feature_extraction.text import CountVectorizer

# Keep a global model instance so you don’t retrain every time
topic_model = None

def train_topic_model(docs: List[str]) -> Tuple[List[int], List[float]]:
    """
    Fits the BERTopic model to the input documents.
    Returns a tuple of (topic assignments for each doc, topic confidence probabilities).
    """
    global topic_model
    vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words="english")
    topic_model = BERTopic(vectorizer_model=vectorizer_model, language="english")
    topics, probs = topic_model.fit_transform(docs)
    return topics, probs


def get_topic_info() -> Any:
    """
    Returns topic summary (including size, keywords) from the trained model.
    """
    if topic_model is None:
        raise ValueError("Model has not been trained yet.")
    return topic_model.get_topic_info()


def get_docs_for_topic(topic_id: int) -> Any:
    """
    Returns documents associated with a specific topic.
    """
    if topic_model is None:
        raise ValueError("Model has not been trained yet.")
    return topic_model.get_representative_docs()[topic_id]


# ✅ Add this new function — fixes your ImportError
def summarize_topics() -> list:
    """
    Generates a human-readable summary of the topics using BERTopic.
    """
    if topic_model is None:
        raise ValueError("Model has not been trained yet.")

    topic_info = topic_model.get_topic_info()
    summaries = []

    for _, row in topic_info.iterrows():
        topic_id = row["Topic"]
        keywords = row["Name"]
        summaries.append(f"Topic {topic_id}: {keywords}")

    return summaries
