import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
 
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/dekanat.db")
DATABASE_URL = f"sqlite:///./{DATABASE_PATH}"
 
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
 
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
 
 
class Base(DeclarativeBase):
    pass


def get_db():
    """Генератор сесій бази даних для Dependency Injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
