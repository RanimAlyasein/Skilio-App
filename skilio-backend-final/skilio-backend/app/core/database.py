"""
app/core/database.py
────────────────────
SQLAlchemy engine, session factory, and declarative Base.

Auto-adapts to SQLite, MySQL, and PostgreSQL based on DATABASE_URL.
SQLite requires check_same_thread=False and no pool_recycle.
MySQL/PostgreSQL get connection timeouts so startup fails fast.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import get_settings

settings = get_settings()

# ── Engine kwargs differ per database type ────────────────────────────────────
if settings.is_sqlite:
    _engine_kwargs = {
        "connect_args": {"check_same_thread": False},  # required for FastAPI
        "pool_pre_ping": True,
    }
else:
    _engine_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "connect_args": {"connect_timeout": 5},        # fail fast if DB unreachable
    }

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    **_engine_kwargs,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def check_db_connection() -> bool:
    """
    Verify the DB is reachable at startup.
    Prints a helpful message and raises on failure.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        db_type = "SQLite" if settings.is_sqlite else ("MySQL" if settings.is_mysql else "PostgreSQL")
        raise RuntimeError(
            f"\n\n  ✗ Cannot connect to {db_type}.\n"
            f"  DATABASE_URL = {settings.database_url}\n\n"
            f"  SQLite: check file permissions and that the directory is writable.\n"
            f"  MySQL/PostgreSQL: ensure the server is running and credentials are correct.\n\n"
            f"  Error: {exc}\n"
        ) from exc
