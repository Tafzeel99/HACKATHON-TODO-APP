"""Database connection and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from src.config import get_settings

settings = get_settings()

# Create async engine with connection pooling
# SQLite doesn't support pool_size/max_overflow, so only add for PostgreSQL
engine_kwargs: dict = {
    "echo": settings.is_development,
}

if "sqlite" not in settings.database_url:
    # PostgreSQL (Neon) settings with SSL
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
        "connect_args": {"ssl": ssl_context},
    })
else:
    # SQLite specific settings
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(
    settings.async_database_url,
    **engine_kwargs,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
