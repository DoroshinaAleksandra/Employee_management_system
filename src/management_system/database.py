"""
Database connection setup.
Uses SQLite.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Database URL: creates employees.db file in the project root
# SQLite will automatically create the file if it doesn't exist
SQLALCHEMY_DATABASE_URL = "sqlite:///./employees.db"

# Create database engine/connection
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session factory for database operations
SessionLocal = sessionmaker( # pylint: disable=invalid-name
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models (all tables inherit from this)
Base = declarative_base()


def init_db() -> None:
    """
    Create all tables defined in models.py (if they don't exist yet).
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """
    Session generator for dependency injection.
    Ensures session is closed even if an error occurs (pattern for web frameworks).
    """
    db = SessionLocal()
    try:
        yield db  # type: ignore
    finally:
        db.close()
