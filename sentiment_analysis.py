
# Import the sentiment-analysis pipeline from Hugging Face
from transformers import pipeline

# ------------------------------------------
# Load the Model Once When the App Starts
# ------------------------------------------
# The "pipeline" function creates a simple interface over complex transformer models.
# Here we load 'distilbert-base-uncased-finetuned-sst-2-english',
# which is fine-tuned for binary sentiment classification (positive/negative).

print("🔧 Loading sentiment analysis model (DistilBERT)...")
sentiment_analyzer = pipeline(
    task="sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)
print("✅ Sentiment model loaded successfully.")

# ------------------------------------------
# Function: analyze_sentiment(text: str)
# ------------------------------------------
def analyze_sentiment(text: str) -> dict:

    if not text:
        return {"label": "EMPTY", "score": 0.0}

    # Use the Hugging Face model to perform inference
    results = sentiment_analyzer(text)

    # Results come as a list like: [{'label': 'POSITIVE', 'score': 0.998}]
    result = results[0]

    # Optional: make label lowercase and round score for readability
    return {
        "label": result["label"].capitalize(),
        "confidence": round(result["score"], 4)
    }


"""
Analyze the sentiment of the provided text.

Steps performed:
    1. Pass the text to the loaded model.
    2. Receive output in the form of label and confidence score.
Returns:
    A dictionary containing the sentiment label (POSITIVE / NEGATIVE)
    and a confidence score.
"""