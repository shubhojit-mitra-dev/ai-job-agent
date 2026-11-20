"""SQLAlchemy asynchronous engine and session lifecycle."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, Pool

from app.core.config import settings


def get_engine_pool(pool_name: str) -> type[Pool] | None:
    """Resolve pool class based on configuration."""
    if pool_name == "NullPool":
        return NullPool
    return None  # SQLAlchemy uses default QueuePool when poolclass is None


# Enforce statement_cache_size=0 for Supabase / PgBouncer transaction pooling
connect_args = {"statement_cache_size": settings.DB_STATEMENT_CACHE_SIZE}

engine_kwargs = {
    "echo": settings.APP_ENV == "development",
    "connect_args": connect_args,
}

resolved_pool = get_engine_pool(settings.DB_POOL_CLASS)
if resolved_pool is not None:
    engine_kwargs["poolclass"] = resolved_pool

async_engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs,
)

async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency yielding a transaction-safe async database session."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
