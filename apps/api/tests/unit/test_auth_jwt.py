"""Unit tests for Supabase JWT verification and cryptographic security rules."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import verify_supabase_jwt


@pytest.fixture(scope="module")
def rsa_key_pair() -> tuple[rsa.RSAPrivateKey, str]:
    """Generate ephemeral RSA private and public key pair for asymmetric JWT tests."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return private_key, pem_public


def create_token(
    private_key: rsa.RSAPrivateKey,
    headers: dict[str, Any] | None = None,
    claims: dict[str, Any] | None = None,
) -> str:
    """Helper creating signed RS256 token with default valid claims."""
    now = datetime.now(UTC)
    default_headers: dict[str, Any] = {"alg": "RS256", "kid": "test-key-id", "typ": "JWT"}
    default_claims: dict[str, Any] = {
        "iss": settings.supabase_issuer,
        "aud": settings.SUPABASE_JWT_AUDIENCE,
        "sub": str(uuid.uuid4()),
        "email": "candidate@example.com",
        "role": "authenticated",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
    }
    if headers:
        default_headers.update(headers)
    if claims:
        default_claims.update(claims)

    return jwt.encode(
        payload=default_claims,
        key=private_key,
        algorithm="RS256",
        headers=default_headers,
    )


def test_verify_valid_asymmetric_jwt(rsa_key_pair: tuple[rsa.RSAPrivateKey, str]) -> None:
    private_key, pem_public = rsa_key_pair
    token = create_token(private_key)

    mock_signing_key = MagicMock()
    mock_signing_key.key = pem_public

    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

    with patch("app.core.security.get_jwks_client", return_value=mock_jwks_client):
        payload = verify_supabase_jwt(token)
        assert payload["email"] == "candidate@example.com"
        assert payload["role"] == "authenticated"
        assert "sub" in payload


def test_verify_expired_jwt(rsa_key_pair: tuple[rsa.RSAPrivateKey, str]) -> None:
    private_key, pem_public = rsa_key_pair
    past = datetime.now(UTC) - timedelta(hours=2)
    token = create_token(
        private_key,
        claims={"exp": int(past.timestamp()), "iat": int((past - timedelta(hours=1)).timestamp())},
    )

    mock_signing_key = MagicMock()
    mock_signing_key.key = pem_public
    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

    with patch("app.core.security.get_jwks_client", return_value=mock_jwks_client):
        with pytest.raises(HTTPException) as exc_info:
            verify_supabase_jwt(token)
        assert exc_info.value.status_code == 401


def test_verify_invalid_issuer(rsa_key_pair: tuple[rsa.RSAPrivateKey, str]) -> None:
    private_key, pem_public = rsa_key_pair
    token = create_token(private_key, claims={"iss": "https://malicious.issuer.com"})

    mock_signing_key = MagicMock()
    mock_signing_key.key = pem_public
    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

    with patch("app.core.security.get_jwks_client", return_value=mock_jwks_client):
        with pytest.raises(HTTPException) as exc_info:
            verify_supabase_jwt(token)
        assert exc_info.value.status_code == 401


def test_verify_invalid_audience(rsa_key_pair: tuple[rsa.RSAPrivateKey, str]) -> None:
    private_key, pem_public = rsa_key_pair
    token = create_token(private_key, claims={"aud": "wrong-audience"})

    mock_signing_key = MagicMock()
    mock_signing_key.key = pem_public
    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

    with patch("app.core.security.get_jwks_client", return_value=mock_jwks_client):
        with pytest.raises(HTTPException) as exc_info:
            verify_supabase_jwt(token)
        assert exc_info.value.status_code == 401


def test_verify_missing_sub_claim(rsa_key_pair: tuple[rsa.RSAPrivateKey, str]) -> None:
    private_key, pem_public = rsa_key_pair
    now = datetime.now(UTC)
    token = jwt.encode(
        payload={
            "iss": settings.supabase_issuer,
            "aud": settings.SUPABASE_JWT_AUDIENCE,
            "exp": int((now + timedelta(hours=1)).timestamp()),
        },
        key=private_key,
        algorithm="RS256",
        headers={"alg": "RS256", "kid": "test-key-id"},
    )

    mock_signing_key = MagicMock()
    mock_signing_key.key = pem_public
    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

    with patch("app.core.security.get_jwks_client", return_value=mock_jwks_client):
        with pytest.raises(HTTPException) as exc_info:
            verify_supabase_jwt(token)
        assert exc_info.value.status_code == 401


def test_verify_non_uuid_sub_claim(rsa_key_pair: tuple[rsa.RSAPrivateKey, str]) -> None:
    private_key, pem_public = rsa_key_pair
    token = create_token(private_key, claims={"sub": "not-a-valid-uuid"})

    mock_signing_key = MagicMock()
    mock_signing_key.key = pem_public
    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

    with patch("app.core.security.get_jwks_client", return_value=mock_jwks_client):
        with pytest.raises(HTTPException) as exc_info:
            verify_supabase_jwt(token)
        assert exc_info.value.status_code == 401


def test_verify_forged_signature(rsa_key_pair: tuple[rsa.RSAPrivateKey, str]) -> None:
    private_key, _ = rsa_key_pair
    attacker_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = create_token(attacker_key)

    _, pem_public = rsa_key_pair
    mock_signing_key = MagicMock()
    mock_signing_key.key = pem_public
    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

    with patch("app.core.security.get_jwks_client", return_value=mock_jwks_client):
        with pytest.raises(HTTPException) as exc_info:
            verify_supabase_jwt(token)
        assert exc_info.value.status_code == 401


def test_verify_disallowed_algorithm() -> None:
    now = datetime.now(UTC)
    token = jwt.encode(
        payload={
            "iss": settings.supabase_issuer,
            "aud": settings.SUPABASE_JWT_AUDIENCE,
            "sub": str(uuid.uuid4()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
        },
        key="super-secret-key-32-bytes-long-for-test",
        algorithm="HS256",
    )

    with (
        patch.object(settings, "APP_ENV", "production"),
        patch.object(settings, "SUPABASE_JWT_SECRET", None),
        pytest.raises(HTTPException) as exc_info,
    ):
        verify_supabase_jwt(token)
    assert exc_info.value.status_code == 401
