import re
import nltk
import spacy
from nltk.corpus import stopwords
from textblob import TextBlob


# Try to import the transformer model
try:
    from transformers import pipeline
    print("🔧 Loading AI correction model (lightweight)...")
    corrector = pipeline("text2text-generation", model="oliverguhr/spelling-correction-english-base")
    USE_AI = True
    print("✅ AI model loaded successfully.")
except Exception as e:
    print("⚠️ Could not load AI correction model, fallback to TextBlob:", e)
    USE_AI = False
    corrector = None

# -----------------------------
# Setup
# -----------------------------
nltk.download("stopwords", quiet=True)
stop_words = set(stopwords.words("english"))

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None
    print("⚠️ spaCy model not found. Run: python -m spacy download en_core_web_sm")

# -----------------------------
# Cleaning + Correction
# -----------------------------
def clean_text(text: str) -> str:
    """Basic cleanup for user input."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def ai_correct_text(text: str) -> str:
    """Try AI-based correction, fallback if model fails."""
    if USE_AI and corrector:
        try:
            result = corrector(text, max_length=128, num_return_sequences=1)
            corrected = result[0]["generated_text"]
            return corrected
        except Exception as e:
            print("⚠️ AI correction failed:", e)
    # fallback correction using TextBlob
    return str(TextBlob(text).correct())

def lemmatize_text(text: str) -> str:
    """Simplify words using spaCy (if available)."""
    if not nlp:
        return text
    doc = nlp(text)
    tokens = [
        token.lemma_.lower()
        for token in doc
        if token.is_alpha and token.text.lower() not in stop_words
    ]
    return " ".join(tokens)

def preprocess_query(query: str) -> str:
    """Full pipeline: cleaning → correction → lemmatization."""
    cleaned = clean_text(query)
    corrected = ai_correct_text(cleaned)
    lemmatized = lemmatize_text(corrected)
    return lemmatized
