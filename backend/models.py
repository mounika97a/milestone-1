from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from datetime import datetime
from sqlalchemy import Text
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)   # only set once
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = relationship("Profile", back_populates="user", uselist=False)


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    age_group = Column(String(50))
    language_pref = Column(String(50))
    bio = Column(Text)
    profile_pic = Column(String(255), nullable=True)   # store file path / URL
    created_at = Column(DateTime, default=datetime.utcnow)  # set only on creation
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="profile")