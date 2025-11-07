# auth.py
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from news_backend.database import get_db
from news_backend.models import PasswordResetToken, User

# Config from environment (avoid hardcoding in prod)
SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-change-me")
ALGORITHM = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "15"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# -------------------- Auth helpers --------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(*, sub: int, email: str, role: Optional[str] = "user") -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(sub),          # always string in JWT
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# auth.py — temporary debugging
from jose import JWTError
from fastapi import HTTPException, status

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        email = payload.get("email")
        if not sub or not email:
            raise ValueError("missing claims")
        user = db.query(User).filter(User.id == int(sub)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError as e:
        print("JWT error:", repr(e))  # TEMP: inspect reason
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


# -------------------- Password reset --------------------
def create_password_reset_token(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    reset_record = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
    db.add(reset_record)
    db.commit()
    db.refresh(reset_record)
    return token

def verify_password_reset_token(token: str, db: Session):
    record = db.query(PasswordResetToken).filter_by(token=token).first()
    if not record or record.expires_at < datetime.utcnow():
        return None
    return record.user_id

def reset_user_password(user_id: int, new_password: str, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    user.hashed_password = hash_password(new_password)
    db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user_id).delete()
    db.commit()
    return True

# -------------------- Routes --------------------
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register_user(request: dict, db: Session = Depends(get_db)):
    email = request.get("email")
    password = request.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=email, hashed_password=hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}

@router.post("/login")
def login_user(request: dict, db: Session = Depends(get_db)):
    email = request.get("email")
    password = request.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Issue token with sub = user.id (matches get_current_user)
    access_token = create_access_token(sub=user.id, email=user.email)
    return {"access_token": access_token, "token_type": "bearer"}
