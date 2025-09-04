from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash
from datetime import datetime

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_profile(db: Session, user_id: int, profile: schemas.ProfileCreate):
    db_profile = models.Profile(**profile.dict(), user_id=user_id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def update_profile(db: Session, user_id: int, profile: schemas.ProfileCreate):
    db_profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()

    if db_profile:
        # update existing profile
        db_profile.name = profile.name
        db_profile.age_group = profile.age_group
        db_profile.language_pref = profile.language_pref
        db_profile.bio = profile.bio
        db_profile.profile_pic = profile.profile_pic
        db_profile.updated_at = datetime.utcnow()
    else:
        # create new profile
        db_profile = models.Profile(
            name=profile.name,
            age_group=profile.age_group,
            language_pref=profile.language_pref,
            bio=profile.bio,
            profile_pic=profile.profile_pic,
            user_id=user_id
        )
        db.add(db_profile)

    db.commit()
    db.refresh(db_profile)
    return db_profile
