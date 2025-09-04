from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from sqlalchemy.orm import Session
import os
from datetime import datetime
from .analysis import readability_scores


from . import database, schemas, crud, auth, models

app = FastAPI()

# ---------------- FILE UPLOAD SETUP ----------------
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve uploads folder as static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ---------------- DB DEPENDENCY ----------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {
        "message": "Welcome to Text Morph API 🚀",
        "endpoints": ["/register", "/login", "/profile", "/docs", "/redoc"]
    }

# ---------------- AUTH ----------------
@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

@app.post("/login")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, request.email)
    if not user or not auth.verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# ---------------- PROFILE ----------------
@app.post("/profile", response_model=schemas.ProfileOut)
def create_or_update_profile(
    request: Request,
    name: str = Form(...),
    age_group: str = Form(...),
    language_pref: str = Form(...),
    bio: str = Form(...),
    email: str = Form(...),
    profile_pic: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Handle file upload
    file_url = None
    if profile_pic:
        file_path = os.path.join(UPLOAD_DIR, profile_pic.filename)
        with open(file_path, "wb") as f:
            f.write(profile_pic.file.read())
        # Save public URL
        file_url = f"{request.base_url}uploads/{profile_pic.filename}"

    # Fetch or create profile
    profile = db.query(models.Profile).filter(models.Profile.user_id == user.id).first()

    if profile:
        # Update profile
        profile.name = name
        profile.age_group = age_group
        profile.language_pref = language_pref
        profile.bio = bio
        if file_url:
            profile.profile_pic = file_url
        profile.updated_at = datetime.utcnow()
    else:
        # Create new profile
        profile = models.Profile(
            name=name,
            age_group=age_group,
            language_pref=language_pref,
            bio=bio,
            profile_pic=file_url,
            user_id=user.id
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile

@app.get("/profile/{email}", response_model=schemas.ProfileOut)
def get_profile(email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    if not user or not user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return user.profile

@app.delete("/profile/{email}")
def delete_profile(email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    if not user or not user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # delete profile
    db.delete(user.profile)
    db.commit()
    return {"message": "Profile deleted successfully"}

@app.post("/readability")
async def analyze_readability(
    text: str = Form(None),
    file: UploadFile = File(None),
):
    """
    Accepts raw text (preferred) or a small .txt file and returns readability metrics.
    """
    if not text and not file:
        raise HTTPException(status_code=400, detail="Provide 'text' or upload a .txt file")

    if file:
        if not file.filename.lower().endswith(".txt"):
            raise HTTPException(status_code=415, detail="Only .txt files are supported for now")
        content = (await file.read()).decode("utf-8", errors="ignore")
    else:
        content = text

    if not content.strip():
        raise HTTPException(status_code=400, detail="Empty text")

    scores = readability_scores(content)
    # derive a coarse level from Flesch Reading Ease
    fk = scores["flesch_kincaid_re"]
    if fk >= 70:
        level = "Beginner"
    elif fk >= 50:
        level = "Intermediate"
    else:
        level = "Advanced"
    scores["level"] = level
    return scores
