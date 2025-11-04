from datetime import datetime, timedelta
import secrets
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# ✅ Import database and models at the top
from news_backend.database import get_db
from news_backend.models import PasswordResetToken, User

SECRET_KEY = "mysupersecretkey12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
RESET_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ==========================================================
# 🔐 Authentication Utility Functions
# ==========================================================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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

# ==========================================================
# 🔁 Password Reset
# ==========================================================
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

# ==========================================================
# 🚀 FastAPI Router
# ==========================================================
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register_user(request: dict, db: Session = Depends(get_db)):
    # ✅ Now get_db is properly recognized
    email = request.get("email")
    password = request.get("password")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(password)
    new_user = User(email=email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}

@router.post("/login")
def login_user(request: dict, db: Session = Depends(get_db)):
    email = request.get("email")
    password = request.get("password")

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
