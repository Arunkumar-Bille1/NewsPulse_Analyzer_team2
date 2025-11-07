# # =========================================================
# # TrendPulse AI Backend - main.py
# # =========================================================
# from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request, Query
#
# #from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from news_backend.trend_detector import detect_trends_from_db
# from sqlalchemy.orm import Session
# from datetime import datetime, timedelta
# from authlib.integrations.starlette_client import OAuth
# from jose import JWTError, jwt
# from passlib.context import CryptContext
# from typing import List
# from pydantic import BaseModel
# from dotenv import load_dotenv
# from transformers import pipeline
# import os
# from news_backend import auth
# from news_backend.text_preprocessor import preprocess_query
#
# # =========================================================
# # Import Local Project Modules
# # =========================================================
# from news_backend.database import Base, engine, get_db
# from news_backend import models, schemas
# from news_backend.auth import router as auth_router
# from news_backend.news_routes import router as news_routes_router
# from news_backend.detect_trends import router as detect_trends_router
# from news_backend.topic_routes import router as topic_routes_router
# from news_backend.topic_modeler import train_topic_model, get_topic_info
# from news_backend.news_fetcher import get_combined_news
# from news_backend.news_fetcher import save_news_to_db
# #from news_backend.detect_trends import detect_trends_from_db
# #from news_backend.detect_trends import router as detect_trends_router
# from news_backend.news_routes import router as news_router
# from news_backend.topic_routes import router as topic_router
# from news_backend.detect_trends import router as detect_trends_router
# from news_backend.supabase_client import supabase, save_news_to_supabase
# # =========================================================
# # FASTAPI INITIALIZATION
# # =========================================================
# app = FastAPI(title="NewsPulse Analyzer")
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from passlib.context import CryptContext
# from supabase import create_client
# import os
# from dotenv import load_dotenv
#
# # Load env and create Supabase client
# load_dotenv()
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# app = FastAPI()
#
#
# # =========================================================
# # ENABLE CORS
# # =========================================================
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # Your frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
#
# # Include routers
# app.include_router(news_router)
# app.include_router(topic_router)
# app.include_router(detect_trends_router)  # ✅ correctly included
#
# # =========================================================
# # ENVIRONMENT & DATABASE SETUP
# # =========================================================
# load_dotenv()
# Base.metadata.create_all(bind=engine)
#
# # =========================================================
# # SECURITY CONFIGURATION
# # =========================================================
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
#
# # =========================================================
# # OAUTH SETUP (Google)
# # =========================================================
# oauth = OAuth()
# oauth.register(
#     name="google",
#     client_id=os.getenv("GOOGLE_CLIENT_ID"),
#     client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
#     server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
#     client_kwargs={"scope": "openid email profile"},
# )
#
# # =========================================================
# # LOAD NLP MODELS (Startup Once)
# # =========================================================
# sentiment_analyzer = pipeline(
#     "sentiment-analysis",
#     model="distilbert-base-uncased-finetuned-sst-2-english"
# )
#
# ner_pipeline = pipeline(
#     "ner",
#     model="dslim/bert-base-NER",
#     aggregation_strategy="simple"
# )
#
# # =========================================================
# # REGISTER ROUTERS
# # =========================================================
# app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# app.include_router(news_routes_router, prefix="/news", tags=["News"])
# app.include_router(detect_trends_router, prefix="/trends", tags=["Trends"])
# app.include_router(topic_routes_router, prefix="/topics", tags=["Topics"])
#
# # =========================================================
# # ADMIN VALIDATION FUNCTION
# # =========================================================
# def require_admin(current_user: models.User = Depends()):
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Admin access required")
#     return current_user
#
# # =========================================================
# # USER REGISTRATION ENDPOINT
# # =========================================================
# # class RegisterRequest(BaseModel):
# #     username: str
# #     email: str
# #     password: str
# #
# #
# # @app.post("/auth/register")
# # def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
# #     from news_backend.models import User
# #
# #     existing_user = db.query(User).filter(User.email == request.email).first()
# #     if existing_user:
# #         raise HTTPException(status_code=400, detail="Email already registered")
# #
# #     hashed_password = pwd_context.hash(request.password)
# #     new_user = User(
# #         username=request.username,
# #         email=request.email,
# #         hashed_password=hashed_password,
# #     )
# #     db.add(new_user)
# #     db.commit()
# #     db.refresh(new_user)
# #     return {"message": "User registered successfully", "user_id": new_user.id}
#
# # =========================================================
# # LOGIN ENDPOINT
# # =========================================================
# # @app.post("/auth/login")
# # def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
# #     user = db.query(models.User).filter(models.User.email == form_data.username).first()
# #     if not user or not pwd_context.verify(form_data.password, user.hashed_password):
# #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
# #     return {"message": "Login successful", "user_id": user.id}
#
# # =========================================================
# # FORGOT PASSWORD ENDPOINT
# # =========================================================
# @app.post("/auth/forgot-password")
# def forgot_password(request: schemas.PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.email == request.email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     background_tasks.add_task(send_reset_email, user.email)
#     return {"message": "Password reset email sent successfully"}
#
# def send_reset_email(email: str):
#     print(f"📧 Sending password reset email to {email}")
#
# # =========================================================
# # TREND DEMO ENDPOINT
# # =========================================================
# @app.get("/detect-trends")
# def detect_trends(range: str = "7d"):
#     topics = [
#         {"name": "AI", "score": 0.89},
#         {"name": "Elections", "score": 0.73},
#     ]
#     result = {"topics": topics}
#     print("🔍 Sending response to frontend:", result)
#     return result
#
# # =========================================================
# # ROOT ENDPOINT
# # =========================================================
# @app.get("/")
# def root():
#     return {"message": "🚀 TrendPulse AI Backend Running Successfully!"}
#
# # =========================================================
# # STARTUP LOG (Show All Routes)
# # =========================================================
# @app.on_event("startup")
# async def show_routes():
#     print("\n✅ Registered routes:")
#     for r in app.routes:
#         print(f" → {r.path}")
#     print("✅ Server Ready!\n")
#
# #
# # @app.post("/login")
# # def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)): # type: ignore
# #     user = db.query(models.User).filter(models.User.email == form_data.username).first()
# #     if not user or not auth.verify_password(form_data.password, user.hashed_password):
# #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
# #                             detail="Invalid username or password")
# #
# #     token = auth.create_access_token(data={"sub": user.email, "role": user.role})
# #     return {"access_token": token, "token_type": "bearer"}
# #
# # def verify_token(token: str = Depends(oauth2_scheme)):
# #     try:
# #         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# #         return payload
# #     except JWTError:
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Invalid or expired token",
# #             headers={"WWW-Authenticate": "Bearer"},
# #         )
#
# @app.get("/protected")
# def protected_route(payload: dict = Depends(verify_token)):
#     return {"message": f"Hello, {payload['sub']}! You accessed a protected route."}
#
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         return email
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#
# @app.get("/users/me")
# def read_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     try:
#         payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
#         email = payload.get("sub")
#         if not email:
#             raise HTTPException(status_code=401, detail="Invalid token")
#
#         user = db.query(models.User).filter(models.User.email == email).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#
#         return user
#
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#
# @app.post("/forgot-password")
# def forgot_password(request: schemas.PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)): # type: ignore
#     token = auth.create_password_reset_token(request.email, db)
#     if token:
#         reset_link = f"http://localhost:3000/reset-password?token={token}"
#         background_tasks.add_task(send_reset_email, request.email, reset_link)
#     return {"message": "If your email exists, a reset link has been sent."}
#
# @app.post("/reset-password")
# def reset_password(request: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
#     user_id = auth.verify_password_reset_token(request.token, db)
#     if not user_id:
#         raise HTTPException(status_code=400, detail="Invalid or expired token.")
#
#     success = auth.reset_user_password(user_id, request.new_password, db)
#     if not success:
#         raise HTTPException(status_code=404, detail="User not found.")
#
#     return {"message": "Password has been successfully reset."}
#
# @app.get("/admin/users", response_model=List[schemas.UserOut], dependencies=[Depends(require_admin)])
# def read_all_users(db: Session = Depends(get_db)):
#     users = db.query(models.User).all()
#     return users
#
# @app.get("/auth/google")
# async def login_via_google(request: Request):
#     redirect_uri = request.url_for("auth_google_callback")
#     return await oauth.google.authorize_redirect(request, redirect_uri)
#
# @app.get("/auth/google/callback")
# async def google_auth_callback(request: Request, db: Session = Depends(get_db)):
#     token = await oauth.google.authorize_access_token(request)
#     user_info = token.get("userinfo")
#
#     if not user_info or not user_info.get("email"):
#         raise HTTPException(status_code=400, detail="Google authentication failed")
#
#     email = user_info["email"]
#     user = db.query(models.User).filter(models.User.email == email).first()
#
#     if not user:
#         user = models.User(
#             email=email,
#             name=user_info.get("name", ""),
#             hashed_password="",
#             role="user"
#         )
#         db.add(user)
#         db.commit()
#         db.refresh(user)
#
#     access_token = auth.create_access_token({"sub": email, "role": user.role})
#     return {"access_token": access_token, "token_type": "bearer"}
#
# @app.get("/admin/dashboard", dependencies=[Depends(require_admin)])
# def admin_dashboard(db: Session = Depends(get_db)):
#     users_count = db.query(models.User).count()
#     return {"message": "Welcome to admin dashboard", "users_count": users_count}
#
# def save_article(db: Session, article):
#     existing = db.query(NewsBase).filter(NewsBase.url == article.get("url")).first()
#     if existing:
#         return
#
#     published = article.get("publishedAt")
#     if published:
#         try:
#             published = datetime.fromisoformat(published.replace("Z", "+00:00"))
#         except Exception:
#             published = datetime.utcnow()
#     else:
#         published = datetime.utcnow()
#
#     news = NewsBase(
#         title=article.get("title"),
#         source=article.get("source", {}).get("name", "Unknown"),
#         publishedAt=published,
#         url=article.get("url", ""),
#         description=article.get("description", ""),
#         image=article.get("image"),
#     )
#     db.add(news)
#     db.commit()
#     db.refresh(news)
#
# # @app.get("/news")
# # def get_news(query: str = "technology", db: Session = Depends(get_db)):
# #     processed_query = preprocess_query(query)
# #     articles = get_combined_news(processed_query)
# #     save_news_to_db(db, articles)
# #     return {
# #         "original_query": query,
# #         "processed_query": processed_query,
# #         "articles": articles
# #     }
#
#
#
# # ===========================================================
# # Initialize FastAPI
# # ===========================================================
# app = FastAPI(
#     title="📰 NewsPulse Analyzer API",
#     description="Backend for automated news trend detection and sentiment analysis.",
#     version="1.0.0"
# )
#
# # ===========================================================
# # CORS Configuration
# # ===========================================================
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # Replace * with specific frontend URL in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # ===========================================================
# # Root Endpoint
# # ===========================================================
# @app.get("/")
# def root():
#     return {"message": "🚀 NewsPulse Analyzer Backend Running Successfully!"}
#
#
# # ===========================================================
# # 1️⃣ Text Preprocessing
# # ===========================================================
# @app.post("/process_text")
# def process_text(input_text: str):
#     """
#     Cleans, corrects, and lemmatizes input text.
#     """
#     if not input_text:
#         raise HTTPException(status_code=400, detail="No text provided.")
#     processed = preprocess_query(input_text)
#     return {"original": input_text, "processed": processed}
#
#
# # ===========================================================
# # 2️⃣ Detect Trending Topics from DB
# # ===========================================================
# @app.get("/detect-trends")
# def detect_trends():
#     """
#     Detect trending topics and keywords from the database.
#     """
#     return detect_trends_from_db()
#
#
# # ===========================================================
# # 3️⃣ Topic Modeling (Train and Retrieve Topics)
# # ===========================================================
# @app.post("/train_topics")
# def train_topics(db: Session = Depends(get_db)):
#     """
#     Train BERTopic on all news articles stored in DB.
#     """
#     articles = db.query(models.NewsBase).all()
#     if not articles:
#         raise HTTPException(status_code=404, detail="No news data found in database.")
#
#     docs = [a.title or "" for a in articles]
#     topics, probs = train_topic_model(docs)
#     topic_info = get_topic_info()
#
#     return {"topics": topics, "probabilities": probs, "topic_info": topic_info}
#
#
# # ===========================================================
# # 4️⃣ Health Check
# # ===========================================================
# @app.get("/health")
# def health_check():
#     return {"status": "ok"}
#
#
# # ===========================================================
# # Helper: Clean Keywords
# # ===========================================================
# def clean_keywords(name_field):
#     """
#     Cleans topic keywords from BERTopic's name field.
#     Handles both comma- and underscore-separated cases.
#     """
#     import re
#     name_field = re.sub(r'^\d+_', '', name_field)
#     tokens = [t.strip() for t in name_field.split(',')]
#     if len(tokens) == 1 and '_' in tokens[0]:
#         tokens = [t.strip() for t in tokens[0].split('_')]
#     return [t for t in tokens if t]
#
#
# # ===========================================================
# # 5️⃣ Fetch and Analyze News (Live + Topic Modeling)
# # ===========================================================
# # @app.get("/news")
# # def get_news(query: str = "technology", db: Session = Depends(get_db)):
# #     # Step 1: Clean and preprocess user query
# #     processed_query = preprocess_query(query)
# #
# #     # Step 2: Fetch news articles
# #     articles = get_combined_news(processed_query)
# #
# #     # Step 3: Save to database
# #     save_news_to_db(db, articles)
# #
# #     # Step 4: Prepare valid documents (titles or content only)
# #     docs = [
# #         str(a.get("content") or a.get("description") or a.get("title", ""))
# #         for a in articles
# #         if isinstance(a, dict) and (a.get("title") or a.get("content"))
# #     ]
# #
# #     if not docs:
# #         raise HTTPException(status_code=400, detail="No valid text found for topic modeling.")
# #
# #     # Step 5: Train BERTopic model
# #     topics, probs = train_topic_model(docs)
# #
# #     # Step 6: Get topic details
# #     topic_info_df = get_topic_info()
# #
# #     # Step 7: Map topics to readable keyword labels
# #     topic_map = {
# #         str(row["Topic"]): clean_keywords(row["Name"])
# #         for _, row in topic_info_df.iterrows()
# #     }
# #
# #     # Step 8: Attach topic info to each article
# #     for idx, article in enumerate(articles):
# #         topic_id = str(topics[idx])
# #         keywords = topic_map.get(topic_id, [])
# #         article["topic_id"] = int(topic_id) if topic_id != "-1" else None
# #         article["topic_label"] = keywords[0] if keywords else ""
# #         article["keywords"] = keywords
# #         article["topic_confidence"] = (
# #             float(probs[idx]) if probs is not None and len(probs) > idx else None
# #         )
# #
# #     # Step 9: Return response
# #     return {
# #         "original_query": query,
# #         "processed_query": processed_query,
# #         "articles": articles
# #     }
#
#
#
#
#
#
#
#
# @app.get("/news")
# def get_news(query: str = "technology"):
#     processed_query = preprocess_query(query)
#     articles = get_combined_news(processed_query)
#     # Save articles using Supabase API instead of local DB session
#     save_news_to_supabase(articles)
#
#     docs = [
#         str(a.get("content") or a.get("description") or a.get("title", ""))
#         for a in articles if isinstance(a, dict) and (a.get("title") or a.get("content"))
#     ]
#
#     if not docs:
#         raise HTTPException(status_code=400, detail="No valid text found for topic modeling.")
#
#     topics, probs = train_topic_model(docs)
#     # The rest of your topic modeling code remains as is, assuming it works with docs
#
#     # For topic_info_df and keyword mapping, use Supabase if you currently store those in DB
#     # Otherwise, keep local code as before
#
#     # ... (topic_map, attach info to articles, etc.)
#
#     return {
#         "original_query": query,
#         "processed_query": processed_query,
#         "articles": articles
#     }
#
#
#
#
#
#
#
#
#
# # ===========================================================
# # 6️⃣ Fetch Stored News
# # ===========================================================
# @app.get("/news_stored")
# def get_stored_news(db: Session = Depends(get_db)):
#     return db.query(NewsBase).all()
#
#
# # ===========================================================
# # 7️⃣ Keyword Extraction
# # ===========================================================
# @app.get("/extract-keywords")
# def extract_keywords(text: str = Query(...), top_n: int = 5):
#     """
#     Extract top keywords from input text using KeyBERT.
#     """
#     keywords = kw_model.extract_keywords(
#         text,
#         keyphrase_ngram_range=(1, 2),
#         stop_words='english',
#         top_n=top_n
#     )
#     return {"keywords": [{"word": kw[0], "score": float(kw[1])} for kw in keywords]}
#
#
# # ===========================================================
# # 8️⃣ Trending Topics (Latest)
# # ===========================================================
# @app.get("/trending")
# def fetch_trending_data(db: Session = Depends(get_db)):
#     """
#     Fetch latest trending topics and keywords from the database.
#     """
#     return get_latest_trends(db)
#
#
# # ===========================================================
# # 9️⃣ User Profile Management
# # ===========================================================
# @app.post("/profile", response_model=schemas.UserProfileResponse)
# def create_profile(
#     data: schemas.UserProfileCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(auth.get_current_user)
# ):
#     """
#     Create a user profile if not already existing.
#     """
#     existing = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Profile already exists. Use PUT to update.")
#     profile = models.UserProfile(user_id=current_user.id, **data.dict())
#     db.add(profile)
#     db.commit()
#     db.refresh(profile)
#     return profile
#
#
# @app.get("/profile", response_model=schemas.UserProfileResponse)
# def get_profile(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
#     profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
#     return profile
#
#
# @app.put("/profile", response_model=schemas.UserProfileResponse)
# def update_profile(
#     data: schemas.UserProfileUpdate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(auth.get_current_user)
# ):
#     profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
#     for key, value in data.dict(exclude_unset=True).items():
#         setattr(profile, key, value)
#     profile.updated_at = datetime.utcnow()
#     db.commit()
#     db.refresh(profile)
#     return profile
#
#
# @app.delete("/profile")
# def delete_profile(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
#     profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
#     db.delete(profile)
#     db.commit()
#     return {"message": "Profile deleted successfully"}
#
#
# # ===========================================================
# # 🔟 NLP Endpoints: Preprocess, Sentiment, and NER
# # ===========================================================
# @app.get("/preprocess")
# def preprocess_text_endpoint(query: str = Query(..., description="Text to preprocess")):
#     processed = preprocess_query(query)
#     return {"original": query, "processed": processed}
#
#
# @app.get("/sentiment")
# def sentiment_endpoint(text: str = Query(..., description="Text for sentiment analysis")):
#     cleaned_text = preprocess_query(text)
#     result = sentiment_analyzer(cleaned_text)
#
#     if not result:
#         return {"sentiment": {"label": "UNKNOWN", "confidence": 0.0}}
#
#     all_scores = {}
#     result_scores = sentiment_analyzer(cleaned_text, return_all_scores=True)
#
#     if isinstance(result_scores, list) and len(result_scores) > 0:
#         all_scores = {x['label']: float(x['score']) for x in result_scores[0]}
#     else:
#         all_scores = {result[0]['label']: float(result[0]['score'])}
#
#     res = result[0]
#     return {
#         "sentiment": {
#             "label": res["label"].capitalize(),
#             "confidence": round(res["score"], 4),
#             "all_scores": all_scores
#         }
#     }
#
#
# @app.get("/ner")
# def named_entity_recognition(text: str = Query(..., description="Text for entity extraction")):
#     entities = ner_pipeline(text)
#     ner_results = [
#         {
#             "word": ent["word"],
#             "label": ent["entity_group"],
#             "score": float(ent["score"]),
#             "start": ent["start"],
#             "end": ent["end"]
#         }
#         for ent in entities
#     ]
#     return {"entities": ner_results}
#
#
# # ===========================================================
# # 11️⃣ Custom Article Model & News Storage
# # ===========================================================
# class Article(BaseModel):
#     publishedAt: str
#     topic_id: str
#     title: str = ""
#     description: str = ""
#
#
# articles_store = []  # Temporary in-memory storage
#
#
# @app.post("/news/save")
# def save_articles(new_articles: List[Article]):
#     """
#     Save articles and apply topic modeling before storing.
#     """
#     articles = [a.dict() for a in new_articles]
#     docs = [a["title"] for a in articles]
#     topics, probs = train_topic_model(docs)
#     topic_info_df = get_topic_info()
#
#     topic_map = {
#         str(row["Topic"]): clean_keywords(row["Name"])
#         for _, row in topic_info_df.iterrows()
#     }
#
#     for idx, article in enumerate(articles):
#         topic_id = str(topics[idx])
#         keywords = topic_map.get(topic_id, [])
#         article["topic_id"] = topic_id
#         article["topic_label"] = ", ".join(keywords[:2]) if keywords else ""
#         article["keywords"] = keywords
#         article["topic_confidence"] = float(probs[idx]) if probs is not None else None
#         articles_store.append(article)
#
#     return {"status": "articles saved", "count": len(articles_store)}
#
#
# # ===========================================================
# # 12️⃣ Include Routers from Other Modules
# # ===========================================================
# #from news_backend import topic_routes, news_routes, trend_routes
#
# @app.on_event("startup")
# async def show_routes():
#     print("\n✅ Registered routes:")
#     for route in app.routes:
#         print(" →", route.path)
#
# #from news_backend.admin import router as admin_router
# #app.include_router(admin_router)
# from fastapi import FastAPI
#
# #app.include_router(admin_router, prefix="/admin", tags=["Admin"])
#
#
#
#
# # ===========================================================
# # for Supabse end point
# # ===========================================================
# from fastapi.responses import JSONResponse
#
#
#
#
#
#
# @app.get("/news_stored")
# def get_stored_news():
#     response = supabase.table("articles").select("*").order("published_at", desc=True).execute()
#     articles = response.data
#     for article in articles:
#         article["title"] = article.get("title", "")
#         article["description"] = article.get("description", "")
#         article["content"] = article.get("content", "")
#         article["image"] = article.get("image", "")
#         article["url"] = article.get("url", "")
#         article["keywords"] = article.get("keywords", [])
#         article["published_at"] = article.get("published_at") if article.get("published_at") else ""
#     return articles
#
#
#
#
# class RegisterRequest(BaseModel):
#     name: str
#     email: str
#     password: str
#
#
#
# @app.post("/auth/register")
# def register_user(request: RegisterRequest):
#     # Hash password etc.
#     data = {
#         "name": request.name,
#         "email": request.email,
#         "hashed_password": pwd_context.hash(request.password)
#     }
#     try:
#         response = supabase.table("users").insert(data).execute()
#         if not hasattr(response, "data") or len(response.data) == 0:
#             raise HTTPException(status_code=400, detail="Registration failed")
#     except Exception as e:
#         error_msg = str(e)
#         if "users_email_key" in error_msg or "duplicate key" in error_msg:
#             raise HTTPException(status_code=400, detail="Email already registered")
#         raise HTTPException(status_code=500, detail="Registration failed: " + error_msg)
#
#
# @app.post("/register")
# def register_user_alias(request: RegisterRequest):
#     return register_user(request)
#
# from pydantic import BaseModel, EmailStr
#
# class LoginRequest(BaseModel):
#     email: str
#     password: str
#
# @app.post("/login")
# def login_alias(request: LoginRequest):
#     return login(request)
#
# @app.post("/auth/login")
# def login(request: LoginRequest):
#     users = supabase.table("users").select("*").eq("email", request.email).execute().data
#     if not users:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     user = users[0]
#     if not pwd_context.verify(request.password, user["hashed_password"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return {"message": "Login successful", "user_id": user["id"], "name": user["name"]}




























# =========================================================
# TrendPulse AI Backend - main.py (Supabase-first)
# =========================================================

# 1. Load environment FIRST
from dotenv import load_dotenv
load_dotenv()

# 2. Standard library imports
import os
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from collections import Counter
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# 3. Third-party imports
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from pydantic import BaseModel, EmailStr
from transformers import pipeline
from keybert import KeyBERT

# 4. Local modules (AFTER load_dotenv)
from news_backend.text_preprocessor import preprocess_query
from news_backend.topic_modeler import train_topic_model, get_topic_info
from news_backend.news_fetcher import get_combined_news
from news_backend.detect_trends import router as detect_trends_router
from news_backend.topic_routes import router as topic_routes_router
from news_backend.news_routes import router as news_routes_router
from news_backend.supabase_client import (
    supabase,
    save_news_to_supabase,
    fetch_all_articles,
    fetch_articles_batch,
    update_article_keywords
)

# =========================================================
# App init
# =========================================================
app = FastAPI(
    title="📰 NewsPulse Analyzer API",
    description="Backend for automated news trend detection and sentiment analysis.",
    version="1.0.0"
)

# =========================================================
# CORS
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# Security / JWT - SINGLE SOURCE OF TRUTH
# =========================================================
pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_ME_SECRET")
ALGORITHM = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MIN", "60"))

def create_access_token(*, sub: int, email: str, role: str = "user") -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(sub),
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    print("JWT cfg:", ALGORITHM, SECRET_KEY[:6])
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

class CurrentUser(BaseModel):
    id: int
    email: str
    role: str = "user"

def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("sub")
        mail = payload.get("email")
        role = payload.get("role", "user")
        if not uid or not mail:
            raise ValueError("missing sub/email")
        return CurrentUser(id=int(uid), email=mail, role=role)
    except JWTError as e:
        print("JWT decode error:", repr(e))  # Debug log
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

def verify_token(token: str = Depends(oauth2_scheme)):
    """Legacy helper for basic payload access"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_admin(current: CurrentUser = Depends(get_current_user)):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current

# ... rest of your code (Google OAuth, schemas, routes, etc.)


def articles_count():
    r = supabase.table("articles").select("*", count="exact", head=True).execute()
    return r.count

# =========================================================
# Google OAuth (optional)
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
# NLP Pipelines (load once)
# =========================================================
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

# =========================================================
# Schemas
# =========================================================
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class Article(BaseModel):
    publishedAt: str | None = None
    topic_id: str | None = None
    title: str = ""
    description: str = ""

# =========================================================
# Routers from other modules (that don’t depend on SQLite)
# =========================================================
# Keep these if they don’t import SQLAlchemy Session; otherwise update those modules to Supabase.
app.include_router(detect_trends_router, prefix="/trends", tags=["Trends"])
app.include_router(topic_routes_router, prefix="/topics", tags=["Topics"])
app.include_router(news_routes_router, prefix="/news", tags=["News"])  # optional if it’s Supabase-ready

# =========================================================
# Root / Health
# =========================================================
@app.get("/")
def root():
    return {"message": "🚀 NewsPulse Analyzer Backend Running Successfully!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# =========================================================
# Auth with Supabase users table
# =========================================================
from pydantic import BaseModel
from passlib.exc import UnknownHashError

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# POST /auth/register (Supabase)
@app.post("/auth/register")
def register_user(req: RegisterRequest):
    email = (req.email or "").strip().lower()
    if not email or not req.password:
        raise HTTPException(status_code=400, detail="Email and password required")

    # Case-insensitive uniqueness
    existing = (supabase.table("users")
                .select("id")
                .ilike("email", email)
                .limit(1).execute()).data
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        hashed = pwd_context.hash(req.password)
    except Exception as e:
        print("REGISTER hash error:", repr(e))
        raise HTTPException(status_code=400, detail="Password hashing failed")

    data = {"name": req.name or "", "email": email, "hashed_password": hashed, "role": "user"}
    resp = supabase.table("users").insert(data).execute()
    if getattr(resp, "error", None):
        print("REGISTER insert error:", resp.error)
        raise HTTPException(status_code=400, detail="Registration failed")

    created = resp.data[0]
    token = create_access_token(sub=created["id"], email=created["email"], role=created.get("role", "user"))
    return {"message": "User registered successfully", "user_id": created["id"],
            "access_token": token, "token_type": "bearer"}

    created = response.data[0]
    token = create_access_token(sub=created["id"], email=created["email"], role=created.get("role", "user"))
    return {
        "message": "Registration successful",
        "user_id": created["id"],
        "access_token": token,
        "token_type": "bearer"
    }

# POST /auth/login (Supabase)
@app.post("/auth/login")
def login(request: LoginRequest):
    email = (request.email or "").strip().lower()
    users = (supabase.table("users")
             .select("*")
             .ilike("email", email)     # case-insensitive
             .limit(1).execute()).data
    print("LOGIN lookup:", email, "found:", len(users))
    if not users:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = users[0]
    stored = user.get("hashed_password") or ""
    try:
        if not stored or not pwd_context.verify(request.password, stored):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(sub=user["id"], email=user["email"], role=user.get("role","user"))
    return {"message":"Login successful","user_id":user["id"],"name":user.get("name",""),
            "access_token":token,"token_type":"bearer"}


# Legacy alias so frontend can keep calling /login
@app.post("/login")
def login_alias(request: LoginRequest):
    return login(request)



@app.get("/protected")
def protected_route(payload: dict = Depends(verify_token)):
    return {"message": f"Hello, {payload['sub']}! You accessed a protected route."}

# Google OAuth flow -> creates user if missing, returns JWT
@app.get("/auth/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for("auth_google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def auth_google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    if not user_info or not user_info.get("email"):
        raise HTTPException(status_code=400, detail="Google authentication failed")

    email = user_info["email"]
    res = supabase.table("users").select("*").eq("email", email).limit(1).execute()
    if not res.data:
        insert = supabase.table("users").insert({
            "email": email,
            "name": user_info.get("name", ""),
            "hashed_password": "",
            "role": "user"
        }).execute()
        user = insert.data[0]
    else:
        user = res.data[0]

    # ✅ FIXED: use named arguments with id as sub
    access_token = create_access_token(
        sub=user["id"],
        email=email,
        role=user.get("role", "user")
    )
    return {"access_token": access_token, "token_type": "bearer"}


# =========================================================
# Password reset (Supabase-backed tokens table)
# =========================================================
from datetime import datetime, timedelta
import secrets
from pydantic import BaseModel, EmailStr
from fastapi import BackgroundTasks
import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


def send_reset_email(email: str, reset_link: str) -> bool:
    """
    Send password reset email using Gmail SMTP with App Password.
    Requires .env:
      SMTP_EMAIL=you@gmail.com
      SMTP_PASSWORD=16_char_app_password
    """
    sender = os.getenv("SMTP_EMAIL")
    app_pw = os.getenv("SMTP_PASSWORD")
    if not sender or not app_pw:
        print("Missing SMTP_EMAIL/SMTP_PASSWORD env vars")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🔐 Password Reset Request"
    msg["From"] = sender
    msg["To"] = email

    html = f"""
    <html>
      <body>
        <p>Click to reset your password (expires in 15 minutes):</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>If you did not request this, you can ignore this email.</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(sender, app_pw)
            s.sendmail(sender, email, msg.as_string())
        return True
    except Exception as e:
        print("SMTP send failed:", e)
        return False

@app.post("/auth/forgot-password")
def forgot_password(request: PasswordResetRequest, background_tasks: BackgroundTasks):
    user_res = (supabase.table("users")
                .select("id,email")
                .eq("email", request.email)
                .limit(1)
                .execute())
    if not user_res.data:
        return {"message": "If your email exists, a reset link has been sent."}

    user = user_res.data[0]
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.utcnow() + timedelta(minutes=15)).isoformat()

    ins = (supabase.table("password_reset_tokens")
           .insert({"user_id": user["id"], "token": token, "expires_at": expires_at})
           .execute())
    if getattr(ins, "error", None):
        raise HTTPException(status_code=500, detail="Failed to create reset token")

    reset_link = f"http://localhost:3000/reset-password?token={token}"
    background_tasks.add_task(send_reset_email, user["email"], reset_link)
    return {"message": "If your email exists, a reset link has been sent."}












@app.post("/auth/reset-password")
def reset_password(request: PasswordResetConfirm):
    # 1) Lookup token
    tok_res = (supabase.table("password_reset_tokens")
               .select("*")
               .eq("token", request.token)
               .limit(1)
               .execute())
    tok = tok_res.data
    if not tok:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    rec = tok[0]

    # 2) Check expiry
    try:
        exp = rec["expires_at"].replace("Z", "")
        if datetime.fromisoformat(exp) < datetime.utcnow():
            # Delete expired token proactively
            supabase.table("password_reset_tokens").delete().eq("id", rec["id"]).execute()
            raise HTTPException(status_code=400, detail="Invalid or expired token.")
    except Exception:
        # If parsing fails, treat as invalid
        supabase.table("password_reset_tokens").delete().eq("id", rec["id"]).execute()
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    # 3) Update password
    hashed = pwd_context.hash(request.new_password)
    supabase.table("users").update({"hashed_password": hashed}).eq("id", rec["user_id"]).execute()

    # 4) Invalidate token (one-time use)
    supabase.table("password_reset_tokens").delete().eq("id", rec["id"]).execute()

    # 5) (Optional) Force re-login by rotating JWTs on next request
    return {"message": "Password has been successfully reset."}




#
# from fastapi import Depends, status
# from fastapi.security import OAuth2PasswordBearer
# from pydantic import BaseModel
# import jwt  # pyjwt
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # match your route[web:387][web:393]
#
# class CurrentUser(BaseModel):
#     id: int
#     email: str
#
# JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
# JWT_ALG = "HS256"
#
# def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
#     try:
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
#         uid = payload.get("sub")
#         mail = payload.get("email")
#         if not uid or not mail:
#             raise ValueError("missing sub/email in token")
#         return CurrentUser(id=int(uid), email=mail)
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(401, detail="Token expired")
#     except Exception as e:
#         print("JWT decode error:", e)  # log for debugging
#         raise HTTPException(401, detail="Invalid token")



class CurrentUser(BaseModel):
    id: int
    email: str
    role: str = "user"

def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("sub")
        mail = payload.get("email")
        role = payload.get("role", "user")
        if not uid or not mail:
            raise ValueError("missing sub/email")
        return CurrentUser(id=int(uid), email=mail, role=role)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")




from fastapi import Depends, HTTPException
# from news_backend.auth import get_current_user

@app.get("/users/me")
def read_me(current: CurrentUser = Depends(get_current_user)):
    return {"id": current.id, "email": current.email}

# main.py (profile schema + endpoints)
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException

class ProfileUpdate(BaseModel):
    preferred_language: Optional[str] = None
    interests: Optional[List[str]] = None  # <-- array/list!
    articles_per_page: Optional[int] = Field(default=None, ge=1, le=200)
    default_sort: Optional[str] = None
    email_notifications: Optional[bool] = None

DEFAULT_PROFILE = {
    "preferred_language": "en",
    "interests": [],  # <-- empty list/array by default
    "articles_per_page": 20,
    "default_sort": "latest",
    "email_notifications": False,
}



@app.get("/profile")
def get_profile(current: CurrentUser = Depends(get_current_user)):
    res = (supabase.table("user_profiles")
           .select("*")
           .eq("user_id", current.id)
           .limit(1)
           .execute())
    row = (res.data or [None])[0]
    if not row:
        # return a default object instead of 404 to keep UI simple
        return {"user_id": current.id, **DEFAULT_PROFILE}
    return row

@app.post("/profile")
def upsert_profile(data: ProfileUpdate, current: CurrentUser = Depends(get_current_user)):
    payload = {"user_id": current.id, **data.dict(exclude_none=True)}
    # ENSURE interests is always a list before upsert
    if "interests" not in payload or not isinstance(payload["interests"], list):
        payload["interests"] = []
    resp = (supabase.table("user_profiles")
            .upsert(payload, on_conflict="user_id")
            .execute())
    if getattr(resp, "error", None):
        raise HTTPException(status_code=500, detail="Failed to save profile")
    return {"ok": True}


@app.put("/profile")
def update_profile(data: ProfileUpdate, current: CurrentUser = Depends(get_current_user)):
    changes = data.dict(exclude_none=True)
    # ENSURE interests is always a list before update
    if "interests" in changes and not isinstance(changes["interests"], list):
        changes["interests"] = []
    if not changes:
        return {"ok": True}
    resp = (supabase.table("user_profiles")
            .update(changes)
            .eq("user_id", current.id)
            .execute())
    if getattr(resp, "error", None):
        raise HTTPException(status_code=500, detail="Failed to update profile")
    return {"ok": True}






# Aliases in main.py after defining /auth/* endpoints

@app.post("/login")
def login_alias(request: LoginRequest):
    return login(request)  # forwards to /auth/login

@app.post("/register")
def register_alias(request: RegisterRequest):
    return register_user(request)  # forwards to /auth/register

@app.post("/forgot-password")
def forgot_alias(req: PasswordResetRequest, background_tasks: BackgroundTasks):
    return forgot_password(req, background_tasks)  # forwards to /auth/forgot-password

@app.post("/reset-password")
def reset_alias(req: PasswordResetConfirm):
    return reset_password(req)  # forwards to /auth/reset-password

@app.get("/stored-news")
def stored_news_alias():
    return get_stored_news()  # forwards to /news_stored














# =========================================================
# News fetching + topic modeling (Supabase persistence)
# =========================================================
def clean_keywords(name_field: str):
    import re
    name_field = re.sub(r'^\d+_', '', name_field)
    tokens = [t.strip() for t in name_field.split(',')]
    if len(tokens) == 1 and '_' in tokens[0]:
        tokens = [t.strip() for t in tokens[0].split('_')]
    return [t for t in tokens if t]

@app.get("/news")
def get_news(query: str = "technology"):
    processed_query = preprocess_query(query)
    articles = get_combined_news(processed_query)

    # Persist articles in Supabase (upsert by url)
    save_news_to_supabase(articles)

    docs = [
        str(a.get("content") or a.get("description") or a.get("title", ""))
        for a in articles
        if isinstance(a, dict) and (a.get("title") or a.get("content"))
    ]
    if not docs:
        raise HTTPException(status_code=400, detail="No valid text found for topic modeling.")

    topics, probs = train_topic_model(docs)
    topic_info_df = get_topic_info()
    topic_map = {str(row["Topic"]): clean_keywords(row["Name"]) for _, row in topic_info_df.iterrows()}

    for idx, article in enumerate(articles):
        topic_id = str(topics[idx])
        keywords = topic_map.get(topic_id, [])
        article["topic_id"] = int(topic_id) if topic_id != "-1" else None
        article["topic_label"] = keywords[0] if keywords else ""
        article["keywords"] = keywords
        article["topic_confidence"] = float(probs[idx]) if probs is not None and len(probs) > idx else None

    return {"original_query": query, "processed_query": processed_query, "articles": articles}

from typing import Optional

@app.get("/news_stored")
def get_stored_news(page: int = 0, page_size: int = 100):
    """
    Offset pagination: page-based browsing with exact count.
    """
    start = page * page_size
    end = start + page_size - 1
    resp = (supabase.table("articles")
            .select("*", count="exact")
            .order("published_at", desc=True)
            .range(start, end)
            .execute())
    return {
        "items": resp.data or [],
        "count": resp.count or 0,
        "page": page,
        "page_size": page_size
    }




from news_backend.supabase_client import fetch_all_articles

@app.get("/news_stored_full")
def get_stored_news_full():
    rows = fetch_all_articles(page_size=1000)
    return rows


# =========================================================
# NLP utilities
# =========================================================
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
    ner_results = [{
        "word": ent["word"],
        "label": ent["entity_group"],
        "score": float(ent["score"]),
        "start": ent["start"],
        "end": ent["end"]
    } for ent in entities]
    return {"entities": ner_results}

# =========================================================
# Startup: list routes
# =========================================================
@app.on_event("startup")
async def show_routes():
    print("\n✅ Registered routes:")
    for r in app.routes:
        print(" →", r.path)
    print("✅ Server Ready!\n")





from typing import Optional

@app.get("/news_stored")
def get_stored_news(page: int = 0, page_size: int = 100):
    """
    Offset pagination: page-based browsing with exact count.
    """
    start = page * page_size
    end = start + page_size - 1
    resp = (supabase.table("articles")
            .select("*", count="exact")
            .order("published_at", desc=True)
            .range(start, end)
            .execute())
    return {
        "items": resp.data or [],
        "count": resp.count or 0,
        "page": page,
        "page_size": page_size
    }


@app.get("/news_stored_cursor")
def news_cursor(
    last_ts: Optional[str] = None,  # ISO timestamp string from previous page's last item
    last_id: Optional[int] = None,  # tie-breaker id from previous page's last item
    limit: int = 100
):
    """
    Keyset pagination: pass last_ts and last_id from previous page's last row.
    Returns the next 'limit' items newer->older.
    """
    q = (supabase.table("articles")
         .select("*")
         .order("published_at", desc=True)
         .order("id", desc=True))

    if last_ts is not None and last_id is not None:
        # Fetch rows strictly older than the cursor; tie-break when timestamps equal
        # PostgREST 'or' condition uses a string; adjust if your client needs URL-encoding.
        q = q.lt("published_at", last_ts).or_(f"published_at.eq.{last_ts},id.lt.{last_id}")

    resp = q.limit(limit).execute()
    items = resp.data or []

    # Next cursor (provide to the client)
    next_cursor = None
    if items:
        tail = items[-1]
        next_cursor = {
            "last_ts": tail.get("published_at"),
            "last_id": tail.get("id")
        }

    return {"items": items, "next_cursor": next_cursor, "limit": limit}


@app.get("/news_count")
def news_count():
    """
    Exact total row count for articles.
    """
    r = supabase.table("articles").select("*", count="exact", head=True).execute()
    return {"count": r.count or 0}


from fastapi import Query
from keybert import KeyBERT

kw_model = KeyBERT()  # load once at startup

@app.get("/extract-keywords")
def extract_keywords(text: str = Query(..., min_length=3), top_n: int = 5):
    kws = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english",
        top_n=top_n,
    )
    return {"keywords": [{"word": w, "score": float(s)} for (w, s) in kws]}




# main.py (or a service module)
from news_backend.supabase_client import fetch_articles_batch, update_article_keywords

@app.post("/extract-keywords/batch")
def extract_keywords_batch(page_size: int = 500, top_n: int = 5):
    processed = 0
    offset = 0
    results = []
    while True:
        batch = fetch_articles_batch(offset, page_size)
        if not batch:
            break
        updates = []
        for a in batch:
            text = " ".join(filter(None, [a.get("title",""), a.get("description",""), a.get("content","")])).strip()
            if not text:
                continue
            kws = kw_model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                stop_words="english",
                top_n=top_n,
            )
            updates.append({"id": a["id"], "keywords": [w for (w, _) in kws]})
            results.append({"id": a["id"], "keywords": [{"word": w, "score": float(s)} for (w, s) in kws]})
        update_article_keywords(updates)
        processed += len(updates)
        if len(batch) < page_size:
            break
        offset += page_size
    return {"updated": processed, "items": results}

from datetime import datetime, timedelta
from collections import Counter
from fastapi import Query

# Helper: fetch recent articles from Supabase by time window
def _days_ago_iso(days: int):
    return (datetime.utcnow() - timedelta(days=days)).isoformat()

def _fetch_recent_articles(days: int):
    since = _days_ago_iso(days)
    resp = (supabase.table("articles")
            .select("id,title,description,content,published_at")
            .gte("published_at", since)
            .order("published_at", desc=True)
            .limit(5000)  # server-side cap; increase if needed
            .execute())
    return resp.data or []

def _basic_tokens(text: str):
    import re
    return [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z\-]{2,}", text or "")]

def _compute_trends(days: int):
    rows = _fetch_recent_articles(days)
    texts = [
        " ".join(filter(None, [r.get("title",""), r.get("description",""), r.get("content","")]))
        for r in rows
    ]
    freq = Counter()
    for t in texts:
        freq.update(_basic_tokens(t))
    # top keywords
    trending_keywords = [{"word": w, "frequency": c} for w, c in freq.most_common(20)]
    # naive topic buckets by most frequent terms (placeholder)
    topics = {}
    for w, _ in freq.most_common(5):
        topics[w] = [w]
    return rows, trending_keywords, topics

def _compute_topic_trends(days: int):
    rows, trending_keywords, topics = _compute_trends(days)
    # sentiment-over-time mock using existing pipeline if available
    by_day = {}
    for r in rows:
        day = (r.get("published_at") or "")[:10] or "Unknown"
        by_day.setdefault(day, {"positive": 0, "neutral": 0, "negative": 0})
        # if you wired sentiment_analyzer earlier, use it here; else bucket as neutral
        by_day[day]["neutral"] += 1
    sentiment_over_time = [
        {"date": k, **v} for k, v in sorted(by_day.items(), key=lambda x: x[0])
    ]
    sentiment_distribution = [
        {"name": "Positive", "value": sum(d["positive"] for d in by_day.values())},
        {"name": "Neutral", "value": sum(d["neutral"] for d in by_day.values())},
        {"name": "Negative", "value": sum(d["negative"] for d in by_day.values())},
    ]
    top_topics = [{"topic": k, "count": len(v)} for k, v in topics.items()]
    return {
        "top_topics": top_topics,
        "sentiment_distribution": sentiment_distribution,
        "sentiment_over_time": sentiment_over_time,
    }

# Alias 1: Trending page expects { trending_keywords, topics }
@app.get("/detect-trends")
def detect_trends(range: str = Query("7d")):
    days = {"7d": 7, "30d": 30, "90d": 90}.get(range, 7)
    _, trending_keywords, topics = _compute_trends(days)
    return {"trending_keywords": trending_keywords, "topics": topics}

# Alias 2: TopicTrends page expects { top_topics, sentiment_distribution, sentiment_over_time }
@app.get("/detect-trends/topics")
def detect_trends_topics(range: str = Query("7d")):
    days = {"7d": 7, "30d": 30, "90d": 90}.get(range, 7)
    return _compute_topic_trends(days)



#=================================================================
# At this point redirect to login essue is solved
#=================================================================