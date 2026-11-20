"""Integration tests for FastAPI health and auth endpoints."""

import uuid
from unittest.mock import patch

import httpx
import pytest

from app.core.config import settings
from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_get_me_without_authorization() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        # HTTPBearer with auto_error=True returns 401 or 403 on missing credentials
        assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_me_with_invalid_token() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_valid_bearer_token() -> None:
    test_user_id = uuid.uuid4()
    mock_payload = {
        "sub": str(test_user_id),
        "email": "engineer@example.com",
        "role": "authenticated",
        "iss": settings.supabase_issuer,
        "aud": settings.SUPABASE_JWT_AUDIENCE,
    }

    with patch("app.modules.auth.dependencies.verify_supabase_jwt", return_value=mock_payload):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": "Bearer valid-mock-token"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == str(test_user_id)
            assert data["email"] == "engineer@example.com"
            assert data["role"] == "authenticated"
