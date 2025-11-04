from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from news_backend.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    country = Column(String, nullable=True)
    language = Column(String, default="English")
    interests = Column(JSON, default=list)
    profile_photo = Column(String, nullable=True)
    role = Column(String, default="user")  
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    preferred_language = Column(String, default="English")
    interests = Column(JSON, default=[])
    articles_per_page = Column(Integer, default=20)
    default_sort = Column(String, default="newest")
    email_notifications = Column(Boolean, default=False)
    trending_alerts = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")

class NewsBase(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=True)
    publishedAt = Column(DateTime, nullable=True)
    url = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    image = Column(String, nullable=True)
    keywords = Column(JSON, default=list)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
