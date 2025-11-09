# news_backend/auth.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from news_backend.supabase_client import supabase

from fastapi import Depends, HTTPException, status
from news_backend.supabase_client import supabase


router = APIRouter(prefix="/auth", tags=["Auth"])

# Secrets / config
SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_ME_SECRET")
ALGORITHM = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
pwd_context = CryptContext(schemes=["bcrypt", "bcrypt_sha256"], deprecated="auto")

# Helpers
def create_access_token(*, sub: int, email: str, role: Optional[str] = "user") -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(sub),
        "email": email,
        "role": role or "user",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Schemas
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class CurrentUser(BaseModel):
    id: int
    email: str
    role: str = "user"

# Routes
@router.post("/register")
def register_user(req: RegisterRequest):
    email = req.email.strip().lower()
    existing = (supabase.table("users")
                .select("id")
                .ilike("email", email)
                .limit(1).execute()).data
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(req.password)
    ins = supabase.table("users").insert({
        "name": req.name or "",
        "email": email,
        "hashed_password": hashed,
        "role": "user"
    }).execute()
    if getattr(ins, "error", None):
        raise HTTPException(status_code=400, detail="Registration failed")
    user = ins.data[0]
    token = create_access_token(sub=user["id"], email=user["email"], role=user.get("role", "user"))
    return {"message": "User registered successfully",
            "user_id": user["id"],
            "access_token": token,
            "token_type": "bearer"}

@router.post("/login")
def login_user(req: LoginRequest):
    email = req.email.strip().lower()
    res = (supabase.table("users")
           .select("*")
           .ilike("email", email)
           .limit(1).execute())
    rows = res.data or []
    if not rows:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = rows[0]
    if not user.get("hashed_password") or not pwd_context.verify(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(sub=user["id"], email=user["email"], role=user.get("role", "user"))
    return {"message": "Login successful",
            "user_id": user["id"],
            "access_token": token,
            "token_type": "bearer"}

# Security deps (use /auth/token so Swagger's OAuth2PasswordBearer works)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    print("get_current_user token_len:", len(token) if token else 0)
    try:
        payload = decode_access_token(token)
        print("JWT sub/email:", payload.get("sub"), payload.get("email"))
        return CurrentUser(
            id=int(payload["sub"]),
            email=payload["email"],
            role=payload.get("role", "user"),
        )
    except Exception as e:
        print("get_current_user decode error:", type(e).__name__, str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")




@router.post("/token")
def login_token(form: OAuth2PasswordRequestForm = Depends()):
    # Enables Swagger “Authorize” popup (username=email, password=password)
    email = form.username.strip().lower()
    res = (supabase.table("users").select("*").ilike("email", email).limit(1).execute())
    rows = res.data or []
    if not rows:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = rows[0]
    if not user.get("hashed_password") or not pwd_context.verify(form.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(sub=user["id"], email=user["email"], role=user.get("role", "user"))
    return {"access_token": token, "token_type": "bearer"}

# news_backend/auth.py


async def require_admin(current: CurrentUser = Depends(get_current_user)):
    # DB check
    res = (supabase.table("users").select("role").eq("id", current.id).limit(1).execute())
    role = (res.data or [{}])[0].get("role", "user")
    print("ADMIN CHECK user_id:", current.id, "db_role:", role)
    if (role or "user").lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current