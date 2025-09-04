from backend.database import engine, Base
from backend import models

# This will create all tables defined in models.py
print("📦 Creating database tables...")

Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully!")
