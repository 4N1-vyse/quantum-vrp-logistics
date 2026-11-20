from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from backend.app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

# Create database session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Base class for database models
class Base(DeclarativeBase):
    pass

# Dependency for FastAPI endpoints
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
