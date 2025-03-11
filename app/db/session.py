from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

# Charger les variables d'environnement
#load_dotenv()

USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
SERVER = os.getenv("DB_SERVER")
DATABASE = os.getenv("DB_NAME")
DRIVER = os.getenv("DB_DRIVER")

DATABASE_URL = f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}:1433/{DATABASE}?driver={DRIVER}"

# Création de l'engine asynchrone
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

# Fonction pour initialiser la base de données
def init_db():
    with engine.begin() as conn:
        conn.run_sync(SQLModel.metadata.create_all)

