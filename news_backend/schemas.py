from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    country: Optional[str] = None
    language: Optional[str] = "English"
    interests: Optional[List[str]] = None
    profile_photo: Optional[str] = None
    role: Optional[str] = "user"
    phone_number: Optional[str] = None

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    country: Optional[str]
    language: Optional[str]
    interests: Optional[List[str]]
    profile_photo: Optional[str]
    phone_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class GoogleAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    name: Optional[str]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class NewsBase(BaseModel):
    title: str
    source: str
    publishedAt: datetime
    url: str
    description: str | None = None
    image: str | None = None
    keywords: List[str] = []
    
    class Config:
        from_attributes = True

class UserProfileBase(BaseModel):
    preferred_language: Optional[str] = "English"
    interests: Optional[List[str]] = []
    articles_per_page: Optional[int] = 20
    default_sort: Optional[str] = "newest"
    email_notifications: Optional[bool] = False
    trending_alerts: Optional[bool] = True

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True