# auth.py — Supabase-only wrapper
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from news_backend.supabase_client import supabase

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-change-me")
ALGORITHM = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
pwd_context = CryptContext(schemes=["bcrypt", "bcrypt_sha256"], deprecated="auto")

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

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register_user(req: RegisterRequest):
    email = req.email.strip().lower()
    # case-insensitive uniqueness
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
    print("REGISTER resp:", getattr(ins, "status_code", None), getattr(ins, "error", None), (ins.data or [])[:1])
    if hasattr(ins, "error") and ins.error:
        raise HTTPException(status_code=400, detail="Registration failed")

    user = ins.data[0]
    token = create_access_token(sub=user["id"], email=user["email"], role=user.get("role", "user"))
    return {"message": "User registered successfully", "user_id": user["id"], "access_token": token, "token_type": "bearer"}

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
    return {"message": "Login successful", "user_id": user["id"], "access_token": token, "token_type": "bearer"}
