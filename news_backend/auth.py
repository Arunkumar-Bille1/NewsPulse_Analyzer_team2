from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import secrets
from sqlalchemy.orm import Session

from news_backend.models import PasswordResetToken, User
from news_backend.database import get_db


SECRET_KEY = "mysupersecretkey12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
RESET_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")


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

