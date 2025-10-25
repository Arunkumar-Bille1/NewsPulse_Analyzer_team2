from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from jose import JWTError, jwt
from datetime import datetime
from dotenv import load_dotenv
from typing import List
import os

from news_backend import auth, schemas, models
from news_backend.database import Base, engine, get_db
from news_backend.auth import SECRET_KEY, ALGORITHM
from news_backend.models import NewsBase
from news_backend.news_fetcher import get_combined_news, save_news_to_db
from news_backend.text_preprocessor import preprocess_query
from news_backend.keyword_extractor import extract_keywords_for_articles
from news_backend.trend_detector import detect_trends_from_db
from news_backend.email_utils import send_reset_email




load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

def require_admin(current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = auth.hash_password(user.password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pw,
        name=user.name,
        country=user.country,
        language=user.language,
        interests=user.interests,
        role=user.role or "user",
        phone_number=user.phone_number,
        profile_photo=user.profile_photo
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
def forgot_password(request: schemas.PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
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


@app.get("/news")
def get_news(query: str = "technology", db: Session = Depends(get_db)):
    processed_query = preprocess_query(query)
    articles = get_combined_news(processed_query)
    save_news_to_db(db, articles)
    
    
    return {
        "original_query": query,
        "processed_query": processed_query,
        "articles": articles
    }


@app.get("/news_stored")
def get_stored_news(db: Session = Depends(get_db)):
    return db.query(NewsBase).all()


@app.get("/extract-keywords")
def extract_keywords():
    return extract_keywords_for_articles(top_n=5)

@app.get("/detect-trends")
def detect_trends():
    return detect_trends_from_db()

@app.post("/profile", response_model=schemas.UserProfileResponse)
def create_profile(data: schemas.UserProfileCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    existing = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists. Use PUT to update.")
    new_profile = models.UserProfile(user_id=current_user.id, **data.dict())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

@app.get("/profile", response_model=schemas.UserProfileResponse)
def get_profile(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.put("/profile", response_model=schemas.UserProfileResponse)
def update_profile(data: schemas.UserProfileUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
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



