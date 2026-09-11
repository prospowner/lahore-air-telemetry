import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Load environment variables first
load_dotenv()

# 2. Fallback to local SQLite if DATABASE_URL isn't explicitly set in your .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lahore_air_local.db")

# 3. Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# 4. Dependency to get DB session in FastAPI paths later
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
