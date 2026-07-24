"""
QuishGuard — Database Connection & Session Management

Production-ready:
- On Render: Uses managed PostgreSQL (DATABASE_URL auto-provided)
- Local dev: Falls back to SQLite if PostgreSQL unavailable
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from loguru import logger

from app.config import settings, _normalize_database_url


async def _detect_database_type() -> str:
    """Detect which database backend is available."""
    db_url = settings.database_url

    # If URL starts with sqlite, use SQLite directly
    if db_url.startswith("sqlite"):
        return "sqlite"

    # Try PostgreSQL connection
    try:
        import asyncpg
        # Convert asyncpg URL to plain postgresql for connection test
        pg_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(pg_url)
        await conn.close()
        return "postgresql"
    except Exception:
        logger.warning("PostgreSQL not available, using SQLite fallback")
        return "sqlite"


async def create_db_engine():
    """Create the async engine based on detected database type."""
    global _engine, _async_session_factory

    db_type = await _detect_database_type()

    if db_type == "postgresql":
        engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
        logger.info(f"✅ PostgreSQL connected: {settings.database_url.split('@')[-1]}")
    else:
        sqlite_url = "sqlite+aiosqlite:///./quishguard_local.db"
        engine = create_async_engine(
            sqlite_url,
            echo=settings.debug,
        )
        logger.info(f"✅ SQLite fallback: quishguard_local.db")

    _async_session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return engine


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# Engine initialized on startup
_engine = None
_async_session_factory = None


async def init_db() -> None:
    """Initialize database — create engine, session factory, and tables."""
    global _engine

    from app.models import Scan, ApiKey  # noqa: F401

    _engine = await create_db_engine()

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
