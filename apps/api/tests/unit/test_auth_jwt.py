"""Unit tests for Supabase JWT verification and cryptographic security rules."""

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from fastapi import HTTPException
from jwt.exceptions import (
    InvalidKeyError,
    PyJWKClientConnectionError,
    PyJWKClientError,
    PyJWKSetError,
)

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


@pytest.fixture(scope="module")
def ec_key_pair() -> tuple[ec.EllipticCurvePrivateKey, str]:
    """Generate ephemeral EC NIST P-256 key pair for ES256 asymmetric JWT tests."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return private_key, pem_public


def create_token(
    private_key: rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey,
    algorithm: str = "RS256",
    headers: dict[str, Any] | None = None,
    claims: dict[str, Any] | None = None,
) -> str:
    """Helper creating signed token with default valid claims."""
    now = datetime.now(UTC)
    default_headers: dict[str, Any] = {"alg": algorithm, "kid": "test-key-id", "typ": "JWT"}
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
        algorithm=algorithm,
        headers=default_headers,
    )


def test_verify_valid_asymmetric_jwt_rs256(rsa_key_pair: tuple[rsa.RSAPrivateKey, str]) -> None:
    private_key, pem_public = rsa_key_pair
    token = create_token(private_key, algorithm="RS256")

    mock_signing_key = MagicMock()
    mock_signing_key.key = pem_public

    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

    with patch("app.core.security.get_jwks_client", return_value=mock_jwks_client):
        payload = verify_supabase_jwt(token)
        assert payload["email"] == "candidate@example.com"
        assert payload["role"] == "authenticated"
        assert "sub" in payload


def test_verify_valid_asymmetric_jwt_es256(
    ec_key_pair: tuple[ec.EllipticCurvePrivateKey, str],
) -> None:
    """Verify ES256 tokens are cryptographically supported and accepted."""
    private_key, pem_public = ec_key_pair
    token = create_token(private_key, algorithm="ES256")

    mock_signing_key = MagicMock()
    mock_signing_key.key = pem_public

    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

    with patch("app.core.security.get_jwks_client", return_value=mock_jwks_client):
        payload = verify_supabase_jwt(token)
        assert payload["email"] == "candidate@example.com"
        assert payload["role"] == "authenticated"
        assert "sub" in payload


def test_verify_jwks_provider_unavailable_returns_503(
    rsa_key_pair: tuple[rsa.RSAPrivateKey, str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify operational network failures during JWKS fetch return controlled 503."""
    private_key, _ = rsa_key_pair
    token = create_token(private_key)

    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.side_effect = PyJWKClientConnectionError(
        "Connection refused to Supabase auth endpoint"
    )

    with (
        patch("app.core.security.get_jwks_client", return_value=mock_jwks_client),
        caplog.at_level(logging.ERROR),
        pytest.raises(HTTPException) as exc_info,
    ):
        verify_supabase_jwt(token)

    assert exc_info.value.status_code == 503
    assert "temporarily unavailable" in exc_info.value.detail
    # Verify token string was NEVER leaked into logs
    assert token not in caplog.text


def test_verify_unknown_kid_returns_401(rsa_key_pair: tuple[rsa.RSAPrivateKey, str]) -> None:
    """Verify unknown or unresolvable key ID returns 401 Unauthorized."""
    private_key, _ = rsa_key_pair
    token = create_token(private_key, headers={"kid": "unknown-ghost-kid"})

    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.side_effect = PyJWKClientError(
        'Unable to find a signing key that matches: "unknown-ghost-kid"'
    )

    with (
        patch("app.core.security.get_jwks_client", return_value=mock_jwks_client),
        pytest.raises(HTTPException) as exc_info,
    ):
        verify_supabase_jwt(token)

    assert exc_info.value.status_code == 401


def test_verify_malformed_jwks_payload_returns_503(
    rsa_key_pair: tuple[rsa.RSAPrivateKey, str],
) -> None:
    """Verify malformed JWKS payload from provider returns controlled 503."""
    private_key, _ = rsa_key_pair
    token = create_token(private_key)

    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.side_effect = PyJWKClientError(
        "The JWKS endpoint did not return a JSON object"
    )

    with (
        patch("app.core.security.get_jwks_client", return_value=mock_jwks_client),
        pytest.raises(HTTPException) as exc_info,
    ):
        verify_supabase_jwt(token)

    assert exc_info.value.status_code == 503
    assert "temporarily unavailable" in exc_info.value.detail


def test_verify_empty_jwks_keys_returns_503(
    rsa_key_pair: tuple[rsa.RSAPrivateKey, str],
) -> None:
    """Verify empty JWKS response from provider returns controlled 503."""
    private_key, _ = rsa_key_pair
    token = create_token(private_key)

    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.side_effect = PyJWKSetError(
        "The JWK Set did not contain any keys"
    )

    with (
        patch("app.core.security.get_jwks_client", return_value=mock_jwks_client),
        pytest.raises(HTTPException) as exc_info,
    ):
        verify_supabase_jwt(token)

    assert exc_info.value.status_code == 503
    assert "temporarily unavailable" in exc_info.value.detail


def test_verify_malformed_key_returns_401(rsa_key_pair: tuple[rsa.RSAPrivateKey, str]) -> None:
    """Verify malformed JWK key returns 401 Unauthorized."""
    private_key, _ = rsa_key_pair
    token = create_token(private_key)

    mock_jwks_client = MagicMock()
    mock_jwks_client.get_signing_key_from_jwt.side_effect = InvalidKeyError("Key format invalid")

    with (
        patch("app.core.security.get_jwks_client", return_value=mock_jwks_client),
        pytest.raises(HTTPException) as exc_info,
    ):
        verify_supabase_jwt(token)

    assert exc_info.value.status_code == 401


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
        headers={"kid": "some-key-id"},
    )

    with (
        patch.object(settings, "APP_ENV", "production"),
        patch.object(settings, "SUPABASE_JWT_SECRET", None),
        pytest.raises(HTTPException) as exc_info,
    ):
        verify_supabase_jwt(token)
    assert exc_info.value.status_code == 401
