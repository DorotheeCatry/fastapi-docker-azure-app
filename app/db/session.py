from sqlmodel import create_engine, Session
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Use SQLite as default if DATABASE_URL is not set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/db/db.sqlite3")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session