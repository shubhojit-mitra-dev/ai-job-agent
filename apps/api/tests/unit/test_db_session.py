"""Tests for database models, engine, and session lifecycle."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.pool import NullPool

from app.db.base import Base, TimestampMixin
from app.db.session import get_db_session, get_engine_pool


def test_get_engine_pool_resolution() -> None:
    assert get_engine_pool("NullPool") is NullPool
    assert get_engine_pool("QueuePool") is None
    assert get_engine_pool("UnknownPool") is None


def test_base_metadata_and_timestamp_mixin() -> None:
    class DummyModel(Base, TimestampMixin):
        __tablename__ = "dummy_models"
        id: Mapped[int] = mapped_column(primary_key=True)

    assert "dummy_models" in Base.metadata.tables
    table = Base.metadata.tables["dummy_models"]
    assert "created_at" in table.c
    assert "updated_at" in table.c
    assert table.c.created_at.nullable is False
    assert table.c.updated_at.nullable is False


@pytest.mark.asyncio
async def test_get_db_session_lifecycle_success() -> None:
    mock_session = AsyncMock()

    with patch("app.db.session.async_session_maker") as mock_maker:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__.return_value = mock_session
        mock_ctx.__aexit__.return_value = None
        mock_maker.return_value = mock_ctx

        sessions = []
        async for session in get_db_session():
            sessions.append(session)

        assert len(sessions) == 1
        assert sessions[0] is mock_session
        mock_session.close.assert_awaited_once()
        mock_session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_db_session_lifecycle_error_rollback() -> None:

    mock_session = AsyncMock()

    with patch("app.db.session.async_session_maker") as mock_maker:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__.return_value = mock_session
        mock_ctx.__aexit__.return_value = None
        mock_maker.return_value = mock_ctx

        gen = get_db_session()
        session = await anext(gen)
        assert session is mock_session

        with pytest.raises(RuntimeError, match="DB simulated failure"):
            await gen.athrow(RuntimeError("DB simulated failure"))

        mock_session.rollback.assert_awaited_once()
        mock_session.close.assert_awaited_once()
