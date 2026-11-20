"""Integration tests for FastAPI health and auth endpoints."""

import uuid
from typing import Any
from unittest.mock import patch

import httpx
import pytest


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: httpx.AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_get_me_without_authorization(async_client: httpx.AsyncClient) -> None:
    response = await async_client.get("/api/v1/auth/me")
    # HTTPBearer with auto_error=True returns 401 or 403 on missing credentials
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_me_with_invalid_token(async_client: httpx.AsyncClient) -> None:
    response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_valid_bearer_token(
    async_client: httpx.AsyncClient,
    mock_user_id: uuid.UUID,
    mock_jwt_payload: dict[str, Any],
) -> None:
    with patch(
        "app.modules.auth.dependencies.verify_supabase_jwt",
        return_value=mock_jwt_payload,
    ):
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer valid-mock-token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(mock_user_id)
        assert data["email"] == "engineer@example.com"
        assert data["role"] == "authenticated"
