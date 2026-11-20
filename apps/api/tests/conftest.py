"""Shared test fixtures for FastAPI application tests."""

import uuid
from collections.abc import AsyncGenerator
from typing import Any

import httpx
import pytest

from app.core.config import settings
from app.main import app
from app.modules.auth.schemas import CurrentUser


@pytest.fixture
def mock_user_id() -> uuid.UUID:
    """Deterministic UUID fixture for tests."""
    return uuid.UUID("11111111-2222-3333-4444-555555555555")


@pytest.fixture
def mock_current_user(mock_user_id: uuid.UUID) -> CurrentUser:
    """Fixture providing a valid CurrentUser instance."""
    return CurrentUser(
        user_id=mock_user_id,
        email="engineer@example.com",
        role="authenticated",
    )


@pytest.fixture
def mock_jwt_payload(mock_user_id: uuid.UUID) -> dict[str, Any]:
    """Fixture providing valid decoded JWT claims payload."""
    return {
        "sub": str(mock_user_id),
        "email": "engineer@example.com",
        "role": "authenticated",
        "iss": settings.supabase_issuer,
        "aud": settings.SUPABASE_JWT_AUDIENCE,
    }


@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Fixture providing an asynchronous HTTP test client bound to the FastAPI app."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
