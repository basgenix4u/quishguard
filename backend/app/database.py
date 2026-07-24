"""
QuishGuard — Database Connection & Session Management

Uses PostgreSQL when available, falls back to SQLite for
local development and testing. The database type is determined
at runtime by attempting a connection.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from loguru import logger

from app.config import settings

# Determine database backend
_db_type = "sqlite"  # Default to SQLite for local dev

# PostgreSQL configuration
_pg_url = settings.database_url
# SQLite fallback
_sqlite_url = "sqlite+aiosqlite:///./quishguard_local.db"


async def _detect_database_type() -> str:
    """Try PostgreSQL connection, fall back to SQLite if unavailable."""
    try:
        import asyncpg
        # Quick connection test
        conn = await asyncpg.connect(_pg_url.replace("postgresql+asyncpg://", "postgresql://"))
        await conn.close()
        return "postgresql"
    except Exception:
        logger.warning("PostgreSQL not available, using SQLite fallback")
        return "sqlite"


async def create_db_engine():
    """Create the async engine based on detected database type."""
    global _db_type

    _db_type = await _detect_database_type()

    if _db_type == "postgresql":
        engine = create_async_engine(
            _pg_url,
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
        logger.info(f"✅ Using PostgreSQL: {_pg_url.split('@')[-1]}")
    else:
        engine = create_async_engine(
            _sqlite_url,
            echo=settings.debug,
        )
        logger.info(f"✅ Using SQLite fallback: quishguard_local.db")

    return engine


# Engine will be initialized on startup
_engine = None
_async_session_factory = None


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def init_db() -> None:
    """Initialize database — create engine, session factory, and all tables."""
    global _engine, _async_session_factory

    # Import all models so they register with Base.metadata
    from app.models import Scan, ApiKey  # noqa: F401

    _engine = await create_db_engine()

    _async_session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables initialized")


async def get_db() -> AsyncSession:
    """Dependency that yields an async database session."""
    if _async_session_factory is None:
        await init_db()

    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
