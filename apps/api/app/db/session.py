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
    """Resolve pool class based on configuration.

    Returns NullPool for serverless Lambda execution or transaction-pooled PgBouncer,
    preventing connection leaks across ephemeral container lifetimes.
    Returns None for continuous local development to let SQLAlchemy use standard QueuePool.
    """
    if pool_name == "NullPool":
        return NullPool
    if pool_name == "QueuePool":
        return None  # None instructs create_async_engine to use standard QueuePool
    return None


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
    """Dependency yielding a transaction-safe async database session.

    Ensures that any unhandled exception within the request scope triggers an explicit
    rollback, and guarantees that the session connection is closed in all execution paths.
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
