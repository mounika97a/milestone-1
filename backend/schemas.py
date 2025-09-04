from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ---------------- PROFILE ----------------
class ProfileBase(BaseModel):
    name: str
    age_group: str
    language_pref: str
    bio: str
    profile_pic: Optional[str] = None  # Will store file path or URL

class ProfileCreate(ProfileBase):
    pass

class ProfileOut(ProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    profile_pic: Optional[str] = None  # Ensure it shows up in API response

    class Config:
        orm_mode = True

# ---------------- USER ----------------
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    name: str
    password: str

class UserOut(UserBase):
    id: int
    name: str
    created_at: datetime
    profile: Optional[ProfileOut] = None

    class Config:
        from_attributes = True

# ---------------- LOGIN ----------------
class LoginRequest(BaseModel):
    email: str
    password: str
