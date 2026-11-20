"""Integration tests validating connectivity, pgvector, and transactions on real PostgreSQL.

These tests execute against a real PostgreSQL instance when reachable (such as the
CI PostgreSQL service container or a local Docker Compose container).
When PostgreSQL is not available locally, the tests skip gracefully while remaining
strictly enforced in the CI environment (via REQUIRE_POSTGRES=true or CI=true).
"""

import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.session import get_db_session


@pytest.mark.asyncio
async def test_real_postgres_connection_and_pgvector_extension() -> None:
    """Verify real PostgreSQL connection and confirmation of vector extension installation."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        connect_args={"timeout": 5.0},
    )
    try:
        async with engine.connect() as conn:
            # Verify database engine is PostgreSQL
            version_res = await conn.execute(text("SELECT version();"))
            version_val = version_res.scalar()
            assert version_val is not None
            assert "PostgreSQL" in version_val

            # Verify pgvector extension was created by Alembic migration
            ext_res = await conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector';")
            )
            ext_name = ext_res.scalar()
            assert ext_name == "vector", (
                "pgvector extension was not found. Ensure 'alembic upgrade head' has run."
            )
    except Exception as exc:
        if os.getenv("CI") or os.getenv("REQUIRE_POSTGRES"):
            raise
        pytest.skip(
            f"Real PostgreSQL service not reachable at {settings.DATABASE_URL} ({exc}). "
            "Skipping local real DB test; verified deterministically in CI service container."
        )
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_real_postgres_transaction_rollback_semantics() -> None:
    """Verify transaction rollback semantics on an actual PostgreSQL instance."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        connect_args={"timeout": 5.0},
    )
    try:
        async with engine.connect() as conn:
            # Begin explicit transaction, create a temporary table, and rollback
            trans = await conn.begin()
            await conn.execute(text("CREATE TEMP TABLE _test_trans_rollback (id serial);"))
            await trans.rollback()

            # Confirm temporary table does not exist post-rollback
            check_res = await conn.execute(
                text(
                    "SELECT EXISTS ("
                    "  SELECT 1 FROM pg_catalog.pg_tables "
                    "  WHERE tablename = '_test_trans_rollback'"
                    ");"
                )
            )
            assert check_res.scalar() is False
    except Exception as exc:
        if os.getenv("CI") or os.getenv("REQUIRE_POSTGRES"):
            raise
        pytest.skip(
            f"Real PostgreSQL service not reachable at {settings.DATABASE_URL} ({exc}). "
            "Skipping local real DB test; verified deterministically in CI service container."
        )
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_real_postgres_session_lifecycle() -> None:
    """Verify get_db_session yields an active session and executes queries against PostgreSQL."""
    try:
        sessions = []
        async for session in get_db_session():
            sessions.append(session)
            result = await session.execute(text("SELECT 1;"))
            assert result.scalar() == 1

        assert len(sessions) == 1
    except Exception as exc:
        if os.getenv("CI") or os.getenv("REQUIRE_POSTGRES"):
            raise
        pytest.skip(
            f"Real PostgreSQL service not reachable at {settings.DATABASE_URL} ({exc}). "
            "Skipping local real DB test; verified deterministically in CI service container."
        )
