from bertopic import BERTopic
from typing import List, Tuple, Any

# Optionally, import sklearn's vectorizer for custom tokenization and stopwords
from sklearn.feature_extraction.text import CountVectorizer

# For performance, reuse the model instance (only train when needed)
topic_model = None

def train_topic_model(docs: List[str]) -> Tuple[List[int], List[float]]:
    """
    Fits the BERTopic model to the input documents.
    Returns a tuple of (topic assignments for each doc, topic confidence probabilities).

    Parameters:
    - docs: List of preprocessed text documents

    Returns:
    - topics: Topic IDs assigned to each document
    - probs: Confidence scores for each assignment
    """
    global topic_model
    # Use a custom vectorizer to remove English stopwords and allow bigrams
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
