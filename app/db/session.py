from sqlmodel import create_engine, Session
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Use SQLite as default if DATABASE_URL is not set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/db/db.sqlite3")

# Create engine with proper error handling
try:
    engine = create_engine(DATABASE_URL, echo=True)
except Exception as e:
    print(f"Error creating database engine: {e}")
    # Fallback to in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", echo=True)

def get_session():
    with Session(engine) as session:
        yield session