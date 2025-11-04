# =========================================================
# TrendPulse AI Backend - main.py
# =========================================================
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request, Query

#from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from news_backend.trend_detector import detect_trends_from_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from authlib.integrations.starlette_client import OAuth
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv
from transformers import pipeline
import os
from news_backend import auth
from news_backend.text_preprocessor import preprocess_query

# =========================================================
# Import Local Project Modules
# =========================================================
from news_backend.database import Base, engine, get_db
from news_backend import models, schemas
from news_backend.auth import router as auth_router
from news_backend.news_routes import router as news_routes_router
from news_backend.detect_trends import router as detect_trends_router
from news_backend.topic_routes import router as topic_routes_router
from news_backend.topic_modeler import train_topic_model, get_topic_info
from news_backend.news_fetcher import get_combined_news
from news_backend.news_fetcher import save_news_to_db
#from news_backend.detect_trends import detect_trends_from_db
#from news_backend.detect_trends import router as detect_trends_router
from news_backend.news_routes import router as news_router
from news_backend.topic_routes import router as topic_router
from news_backend.detect_trends import router as detect_trends_router

# =========================================================
# FASTAPI INITIALIZATION
# =========================================================
app = FastAPI(title="NewsPulse Analyzer")

# =========================================================
# ENABLE CORS
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(news_router)
app.include_router(topic_router)
app.include_router(detect_trends_router)  # ✅ correctly included

# =========================================================
# ENVIRONMENT & DATABASE SETUP
# =========================================================
load_dotenv()
Base.metadata.create_all(bind=engine)

# =========================================================
# SECURITY CONFIGURATION
# =========================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# =========================================================
# OAUTH SETUP (Google)
# =========================================================
oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# =========================================================
# LOAD NLP MODELS (Startup Once)
# =========================================================
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

ner_pipeline = pipeline(
    "ner",
    model="dslim/bert-base-NER",
    aggregation_strategy="simple"
)

# =========================================================
# REGISTER ROUTERS
# =========================================================
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(news_routes_router, prefix="/news", tags=["News"])
app.include_router(detect_trends_router, prefix="/trends", tags=["Trends"])
app.include_router(topic_routes_router, prefix="/topics", tags=["Topics"])

# =========================================================
# ADMIN VALIDATION FUNCTION
# =========================================================
def require_admin(current_user: models.User = Depends()):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# =========================================================
# USER REGISTRATION ENDPOINT
# =========================================================
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


@app.post("/auth/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    from news_backend.models import User

    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(request.password)
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}

# =========================================================
# LOGIN ENDPOINT
# =========================================================
@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.id}

# =========================================================
# FORGOT PASSWORD ENDPOINT
# =========================================================
@app.post("/auth/forgot-password")
def forgot_password(request: schemas.PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    background_tasks.add_task(send_reset_email, user.email)
    return {"message": "Password reset email sent successfully"}

def send_reset_email(email: str):
    print(f"📧 Sending password reset email to {email}")

# =========================================================
# TREND DEMO ENDPOINT
# =========================================================
@app.get("/detect-trends")
def detect_trends(range: str = "7d"):
    topics = [
        {"name": "AI", "score": 0.89},
        {"name": "Elections", "score": 0.73},
    ]
    result = {"topics": topics}
    print("🔍 Sending response to frontend:", result)
    return result

# =========================================================
# ROOT ENDPOINT
# =========================================================
@app.get("/")
def root():
    return {"message": "🚀 TrendPulse AI Backend Running Successfully!"}

# =========================================================
# STARTUP LOG (Show All Routes)
# =========================================================
@app.on_event("startup")
async def show_routes():
    print("\n✅ Registered routes:")
    for r in app.routes:
        print(f" → {r.path}")
    print("✅ Server Ready!\n")


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)): # type: ignore
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")

    token = auth.create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/protected")
def protected_route(payload: dict = Depends(verify_token)):
    return {"message": f"Hello, {payload['sub']}! You accessed a protected route."}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/users/me")
def read_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.post("/forgot-password")
def forgot_password(request: schemas.PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)): # type: ignore
    token = auth.create_password_reset_token(request.email, db)
    if token:
        reset_link = f"http://localhost:3000/reset-password?token={token}"
        background_tasks.add_task(send_reset_email, request.email, reset_link)
    return {"message": "If your email exists, a reset link has been sent."}

@app.post("/reset-password")
def reset_password(request: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    user_id = auth.verify_password_reset_token(request.token, db)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    success = auth.reset_user_password(user_id, request.new_password, db)
    if not success:
        raise HTTPException(status_code=404, detail="User not found.")

    return {"message": "Password has been successfully reset."}

@app.get("/admin/users", response_model=List[schemas.UserOut], dependencies=[Depends(require_admin)])
def read_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@app.get("/auth/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for("auth_google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def google_auth_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info or not user_info.get("email"):
        raise HTTPException(status_code=400, detail="Google authentication failed")

    email = user_info["email"]
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        user = models.User(
            email=email,
            name=user_info.get("name", ""),
            hashed_password="",
            role="user"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = auth.create_access_token({"sub": email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/admin/dashboard", dependencies=[Depends(require_admin)])
def admin_dashboard(db: Session = Depends(get_db)):
    users_count = db.query(models.User).count()
    return {"message": "Welcome to admin dashboard", "users_count": users_count}

def save_article(db: Session, article):
    existing = db.query(NewsBase).filter(NewsBase.url == article.get("url")).first()
    if existing:
        return

    published = article.get("publishedAt")
    if published:
        try:
            published = datetime.fromisoformat(published.replace("Z", "+00:00"))
        except Exception:
            published = datetime.utcnow()
    else:
        published = datetime.utcnow()

    news = NewsBase(
        title=article.get("title"),
        source=article.get("source", {}).get("name", "Unknown"),
        publishedAt=published,
        url=article.get("url", ""),
        description=article.get("description", ""),
        image=article.get("image"),
    )
    db.add(news)
    db.commit()
    db.refresh(news)

# @app.get("/news")
# def get_news(query: str = "technology", db: Session = Depends(get_db)):
#     processed_query = preprocess_query(query)
#     articles = get_combined_news(processed_query)
#     save_news_to_db(db, articles)
#     return {
#         "original_query": query,
#         "processed_query": processed_query,
#         "articles": articles
#     }



# ===========================================================
# Initialize FastAPI
# ===========================================================
app = FastAPI(
    title="📰 NewsPulse Analyzer API",
    description="Backend for automated news trend detection and sentiment analysis.",
    version="1.0.0"
)

# ===========================================================
# CORS Configuration
# ===========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace * with specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================================================
# Root Endpoint
# ===========================================================
@app.get("/")
def root():
    return {"message": "🚀 NewsPulse Analyzer Backend Running Successfully!"}


# ===========================================================
# 1️⃣ Text Preprocessing
# ===========================================================
@app.post("/process_text")
def process_text(input_text: str):
    """
    Cleans, corrects, and lemmatizes input text.
    """
    if not input_text:
        raise HTTPException(status_code=400, detail="No text provided.")
    processed = preprocess_query(input_text)
    return {"original": input_text, "processed": processed}


# ===========================================================
# 2️⃣ Detect Trending Topics from DB
# ===========================================================
@app.get("/detect-trends")
def detect_trends():
    """
    Detect trending topics and keywords from the database.
    """
    return detect_trends_from_db()


# ===========================================================
# 3️⃣ Topic Modeling (Train and Retrieve Topics)
# ===========================================================
@app.post("/train_topics")
def train_topics(db: Session = Depends(get_db)):
    """
    Train BERTopic on all news articles stored in DB.
    """
    articles = db.query(models.NewsBase).all()
    if not articles:
        raise HTTPException(status_code=404, detail="No news data found in database.")

    docs = [a.title or "" for a in articles]
    topics, probs = train_topic_model(docs)
    topic_info = get_topic_info()

    return {"topics": topics, "probabilities": probs, "topic_info": topic_info}


# ===========================================================
# 4️⃣ Health Check
# ===========================================================
@app.get("/health")
def health_check():
    return {"status": "ok"}


# ===========================================================
# Helper: Clean Keywords
# ===========================================================
def clean_keywords(name_field):
    """
    Cleans topic keywords from BERTopic's name field.
    Handles both comma- and underscore-separated cases.
    """
    import re
    name_field = re.sub(r'^\d+_', '', name_field)
    tokens = [t.strip() for t in name_field.split(',')]
    if len(tokens) == 1 and '_' in tokens[0]:
        tokens = [t.strip() for t in tokens[0].split('_')]
    return [t for t in tokens if t]


# ===========================================================
# 5️⃣ Fetch and Analyze News (Live + Topic Modeling)
# ===========================================================
@app.get("/news")
def get_news(query: str = "technology", db: Session = Depends(get_db)):
    # Step 1: Clean and preprocess user query
    processed_query = preprocess_query(query)

    # Step 2: Fetch news articles
    articles = get_combined_news(processed_query)

    # Step 3: Save to database
    save_news_to_db(db, articles)

    # Step 4: Prepare valid documents (titles or content only)
    docs = [
        str(a.get("content") or a.get("description") or a.get("title", ""))
        for a in articles
        if isinstance(a, dict) and (a.get("title") or a.get("content"))
    ]

    if not docs:
        raise HTTPException(status_code=400, detail="No valid text found for topic modeling.")

    # Step 5: Train BERTopic model
    topics, probs = train_topic_model(docs)

    # Step 6: Get topic details
    topic_info_df = get_topic_info()

    # Step 7: Map topics to readable keyword labels
    topic_map = {
        str(row["Topic"]): clean_keywords(row["Name"])
        for _, row in topic_info_df.iterrows()
    }

    # Step 8: Attach topic info to each article
    for idx, article in enumerate(articles):
        topic_id = str(topics[idx])
        keywords = topic_map.get(topic_id, [])
        article["topic_id"] = int(topic_id) if topic_id != "-1" else None
        article["topic_label"] = keywords[0] if keywords else ""
        article["keywords"] = keywords
        article["topic_confidence"] = (
            float(probs[idx]) if probs is not None and len(probs) > idx else None
        )

    # Step 9: Return response
    return {
        "original_query": query,
        "processed_query": processed_query,
        "articles": articles
    }

# ===========================================================
# 6️⃣ Fetch Stored News
# ===========================================================
@app.get("/news_stored")
def get_stored_news(db: Session = Depends(get_db)):
    return db.query(NewsBase).all()


# ===========================================================
# 7️⃣ Keyword Extraction
# ===========================================================
@app.get("/extract-keywords")
def extract_keywords(text: str = Query(...), top_n: int = 5):
    """
    Extract top keywords from input text using KeyBERT.
    """
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words='english',
        top_n=top_n
    )
    return {"keywords": [{"word": kw[0], "score": float(kw[1])} for kw in keywords]}


# ===========================================================
# 8️⃣ Trending Topics (Latest)
# ===========================================================
@app.get("/trending")
def fetch_trending_data(db: Session = Depends(get_db)):
    """
    Fetch latest trending topics and keywords from the database.
    """
    return get_latest_trends(db)


# ===========================================================
# 9️⃣ User Profile Management
# ===========================================================
@app.post("/profile", response_model=schemas.UserProfileResponse)
def create_profile(
    data: schemas.UserProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Create a user profile if not already existing.
    """
    existing = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists. Use PUT to update.")
    profile = models.UserProfile(user_id=current_user.id, **data.dict())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@app.get("/profile", response_model=schemas.UserProfileResponse)
def get_profile(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@app.put("/profile", response_model=schemas.UserProfileResponse)
def update_profile(
    data: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile


@app.delete("/profile")
def delete_profile(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    return {"message": "Profile deleted successfully"}


# ===========================================================
# 🔟 NLP Endpoints: Preprocess, Sentiment, and NER
# ===========================================================
@app.get("/preprocess")
def preprocess_text_endpoint(query: str = Query(..., description="Text to preprocess")):
    processed = preprocess_query(query)
    return {"original": query, "processed": processed}


@app.get("/sentiment")
def sentiment_endpoint(text: str = Query(..., description="Text for sentiment analysis")):
    cleaned_text = preprocess_query(text)
    result = sentiment_analyzer(cleaned_text)

    if not result:
        return {"sentiment": {"label": "UNKNOWN", "confidence": 0.0}}

    all_scores = {}
    result_scores = sentiment_analyzer(cleaned_text, return_all_scores=True)

    if isinstance(result_scores, list) and len(result_scores) > 0:
        all_scores = {x['label']: float(x['score']) for x in result_scores[0]}
    else:
        all_scores = {result[0]['label']: float(result[0]['score'])}

    res = result[0]
    return {
        "sentiment": {
            "label": res["label"].capitalize(),
            "confidence": round(res["score"], 4),
            "all_scores": all_scores
        }
    }


@app.get("/ner")
def named_entity_recognition(text: str = Query(..., description="Text for entity extraction")):
    entities = ner_pipeline(text)
    ner_results = [
        {
            "word": ent["word"],
            "label": ent["entity_group"],
            "score": float(ent["score"]),
            "start": ent["start"],
            "end": ent["end"]
        }
        for ent in entities
    ]
    return {"entities": ner_results}


# ===========================================================
# 11️⃣ Custom Article Model & News Storage
# ===========================================================
class Article(BaseModel):
    publishedAt: str
    topic_id: str
    title: str = ""
    description: str = ""


articles_store = []  # Temporary in-memory storage


@app.post("/news/save")
def save_articles(new_articles: List[Article]):
    """
    Save articles and apply topic modeling before storing.
    """
    articles = [a.dict() for a in new_articles]
    docs = [a["title"] for a in articles]
    topics, probs = train_topic_model(docs)
    topic_info_df = get_topic_info()

    topic_map = {
        str(row["Topic"]): clean_keywords(row["Name"])
        for _, row in topic_info_df.iterrows()
    }

    for idx, article in enumerate(articles):
        topic_id = str(topics[idx])
        keywords = topic_map.get(topic_id, [])
        article["topic_id"] = topic_id
        article["topic_label"] = ", ".join(keywords[:2]) if keywords else ""
        article["keywords"] = keywords
        article["topic_confidence"] = float(probs[idx]) if probs is not None else None
        articles_store.append(article)

    return {"status": "articles saved", "count": len(articles_store)}


# ===========================================================
# 12️⃣ Include Routers from Other Modules
# ===========================================================
#from news_backend import topic_routes, news_routes, trend_routes

@app.on_event("startup")
async def show_routes():
    print("\n✅ Registered routes:")
    for route in app.routes:
        print(" →", route.path)

#from news_backend.admin import router as admin_router
#app.include_router(admin_router)
from fastapi import FastAPI

#app.include_router(admin_router, prefix="/admin", tags=["Admin"])

