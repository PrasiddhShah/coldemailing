"""
Database connection and session management for PostgreSQL/Supabase.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager

# Load environment variables from .env file
load_dotenv()

# Create declarative base for models
Base = declarative_base()


def get_database_url():
    """
    Get database URL from environment.

    Supports:
    - DATABASE_URL: Full connection string (Supabase or any PostgreSQL)
    - Individual DB_* variables for local PostgreSQL

    For Supabase, use the connection string from:
    Project Settings > Database > Connection string > URI
    """
    # Check for full DATABASE_URL first (recommended for Supabase)
    database_url = os.getenv('DATABASE_URL')

    if database_url:
        # Supabase uses 'postgres://' but SQLAlchemy needs 'postgresql://'
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url

    # Fall back to individual variables (local development)
    return (
        f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', 'password')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'apollo_contacts')}"
    )


DATABASE_URL = get_database_url()

# Detect if using Supabase (for connection pool tuning)
IS_SUPABASE = 'supabase' in DATABASE_URL.lower() if DATABASE_URL else False

# Create SQLAlchemy engine with appropriate settings
engine_kwargs = {
    'pool_pre_ping': True,  # Verify connections before using
    'echo': False,  # Set to True for SQL query logging
}

if IS_SUPABASE:
    # Supabase connection pooler settings (use smaller pool for managed DB)
    engine_kwargs.update({
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 1800,  # Recycle connections every 30 min
    })
else:
    # Local PostgreSQL settings
    engine_kwargs.update({
        'pool_size': 10,
        'max_overflow': 20,
    })

engine = create_engine(DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency for FastAPI endpoints to get database session.

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session here
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """
    Context manager for getting database session outside FastAPI.

    Usage:
        with get_db_session() as db:
            # Use db session here
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models.py
    """
    from .models import Base
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def drop_all_tables():
    """
    Drop all database tables.
    WARNING: This will delete all data!
    """
    from .models import Base
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped")


def reset_db():
    """
    Reset database by dropping and recreating all tables.
    WARNING: This will delete all data!
    """
    drop_all_tables()
    init_db()
    print("Database reset complete")


def test_connection():
    """
    Test database connection.
    Returns True if connection successful, False otherwise.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()

        # Extract host info safely (hide password)
        host_info = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'unknown'
        db_type = "Supabase" if IS_SUPABASE else "PostgreSQL"

        print(f"[OK] {db_type} connection successful: {host_info}")
        print(f"[OK] Server version: {version.split(',')[0] if version else 'unknown'}")
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test connection when run directly
    test_connection()
