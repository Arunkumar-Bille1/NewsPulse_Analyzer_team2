
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
from news_backend.admin_routes import router as admin_router  # ok to keep at top

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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)

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
    # fetch additional fields from users table if needed
    res = (supabase.table("users")
           .select("id,email,name,role")
           .eq("id", current.id)
           .limit(1)
           .execute())
    row = (res.data or [None])[0]
    if row:
        return {"id": row["id"], "email": row.get("email", ""), "name": row.get("name", ""), "role": row.get("role", "user")}
    # fallback to token payload if row not found
    return {"id": current.id, "email": current.email, "name": "", "role": current.role}



@app.put("/users/me")
def update_user(data: dict, current: CurrentUser = Depends(get_current_user)):
    changes = {}
    if "name" in data:
        changes["name"] = (data["name"] or "").strip()
    if not changes:
        return {"ok": True}
    supabase.table("users").update(changes).eq("id", current.id).execute()
    return {"ok": True}


# main.py (profile schema + endpoints)
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException

# in main.py
class ProfileUpdate(BaseModel):
    preferred_language: Optional[str] = None
    interests: Optional[List[str]] = None
    articles_per_page: Optional[int] = Field(default=None, ge=1, le=200)
    default_sort: Optional[str] = None
    email_notifications: Optional[bool] = None
    country: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None      # NEW
    phone: Optional[str] = None        # NEW

DEFAULT_PROFILE = {
    "preferred_language": "en",
    "interests": [],
    "articles_per_page": 20,
    "default_sort": "latest",
    "email_notifications": False,
    "country": "",
    "location": "",
    "bio": "",
    "website": "",                      # NEW
    "phone": "",                        # NEW
}




# GET /profile
@app.get("/profile")
def get_profile(current: CurrentUser = Depends(get_current_user)):
    res = (
        supabase.table("user_profiles")
        .select("*")
        .eq("user_id", current.id)
        .limit(1)
        .execute()
    )
    row = (res.data or [None])[0]
    if not row:
        # keep your current behavior: return a default object (no 404)
        return {"user_id": current.id, **DEFAULT_PROFILE}
    return row

# POST /profile -> upsert (create if missing, update if exists)
@app.post("/profile")
def upsert_profile(data: ProfileUpdate, current: CurrentUser = Depends(get_current_user)):
    payload = {"user_id": current.id, **data.dict(exclude_none=True)}

    # ensure types are consistent for jsonb
    if "interests" not in payload or not isinstance(payload["interests"], list):
        payload["interests"] = []

    resp = (
        supabase.table("user_profiles")
        .upsert(payload, on_conflict="user_id")
        .execute()
    )
    # postgrest client raises on error; resp.error may not exist, so be lenient
    if hasattr(resp, "error") and resp.error:
        raise HTTPException(status_code=500, detail="Failed to save profile")
    return {"ok": True}


# PUT /profile -> also upsert (idempotent update that creates when missing)
@app.put("/profile")
def update_profile(data: ProfileUpdate, current: CurrentUser = Depends(get_current_user)):
    changes = data.dict(exclude_none=True)

    if "interests" in changes and not isinstance(changes["interests"], list):
        changes["interests"] = []

    # if there are no changes, do nothing
    if not changes:
        return {"ok": True}

    # use upsert so first save for a new user creates the row
    payload = {"user_id": current.id, **changes}
    resp = (
        supabase.table("user_profiles")
        .upsert(payload, on_conflict="user_id")
        .execute()
    )
    if hasattr(resp, "error") and resp.error:
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



