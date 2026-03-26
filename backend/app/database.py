from __future__ import annotations

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Determine engine options based on database type
is_sqlite = "sqlite" in settings.database_url

# Async engine (for FastAPI)
async_engine_kwargs = {"echo": False}  # Disable SQL echo in production
if not is_sqlite:
    async_engine_kwargs["pool_size"] = 5
    async_engine_kwargs["max_overflow"] = 10
    async_engine_kwargs["pool_pre_ping"] = True
    # Fix for Neon PgBouncer: disable prepared statement cache
    async_engine_kwargs["connect_args"] = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }

async_engine = create_async_engine(settings.database_url, **async_engine_kwargs)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Sync engine (for background tasks)
sync_engine_kwargs = {"echo": False}
if not is_sqlite:
    sync_engine_kwargs["pool_size"] = 5
    sync_engine_kwargs["max_overflow"] = 10
    sync_engine_kwargs["pool_pre_ping"] = True

sync_engine = create_engine(settings.database_url_sync, **sync_engine_kwargs)
SyncSessionLocal = sessionmaker(sync_engine)

# Enable WAL mode for SQLite (better concurrent access)
if is_sqlite:
    @event.listens_for(sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async def create_tables():
    """Create all tables using async engine."""
    from app.models import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully")


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_sync_db():
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
