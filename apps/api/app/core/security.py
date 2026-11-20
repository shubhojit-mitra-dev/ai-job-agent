"""Cryptographic token verification and security utilities."""

import logging
import urllib.error
from typing import Any
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient
from jwt.exceptions import (
    InvalidKeyError,
    InvalidTokenError,
    PyJWKClientConnectionError,
    PyJWKError,
    PyJWKSetError,
    PyJWTError,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

_jwks_client: PyJWKClient | None = None


def get_jwks_client() -> PyJWKClient:
    """Return or initialize cached PyJWKClient for Supabase JWKS endpoint."""
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(
            settings.supabase_jwks_url,
            cache_keys=True,
            max_cached_keys=16,
            cache_jwk_set=True,
            lifespan=3600,
        )
    return _jwks_client


def verify_supabase_jwt(token: str) -> dict[str, Any]:
    """Cryptographically verify a Supabase Auth access token.

    Enforces asymmetric JWKS-based verification (RS256/ES256), exact issuer,
    required audience, expiration, and presence of valid UUID subject.
    Never falls back to symmetric secrets in production environments.
    Distinguishes operational provider errors (503) from invalid credentials (401).
    """
    unauthorized_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    service_unavailable_exc = HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Authentication service temporarily unavailable",
    )

    if not token or not isinstance(token, str):
        raise unauthorized_exc

    # Parse header safely without evaluating unverified claims
    try:
        header = jwt.get_unverified_header(token)
    except PyJWTError as err:
        logger.debug("Failed to parse JWT header: %s", type(err).__name__)
        raise unauthorized_exc from None

    alg = header.get("alg")

    # Non-production test fallback strictly forbidden in production
    if (
        settings.APP_ENV != "production"
        and settings.SUPABASE_JWT_SECRET is not None
        and alg == "HS256"
    ):
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience=settings.SUPABASE_JWT_AUDIENCE,
                issuer=settings.supabase_issuer,
                options={
                    "require": ["exp", "iss", "aud", "sub"],
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iss": True,
                    "verify_aud": True,
                },
            )
            _validate_subject(payload.get("sub"), unauthorized_exc)
            return payload
        except PyJWTError as err:
            logger.debug("Test HMAC verification rejected: %s", type(err).__name__)
            raise unauthorized_exc from None

    # Strict asymmetric algorithm allowlist check
    if alg not in settings.SUPABASE_JWT_ALGORITHMS:
        logger.warning("Rejected token with non-allowlisted algorithm: %s", alg)
        raise unauthorized_exc

    # Key ID claim check
    kid = header.get("kid")
    if not kid:
        logger.warning("Token header missing kid claim")
        raise unauthorized_exc

    # Fetch signing key from cached JWKS provider
    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
    except (
        PyJWKClientConnectionError,
        urllib.error.URLError,
        TimeoutError,
        ConnectionError,
    ) as err:
        logger.error(
            "Supabase JWKS provider unreachable or network error: %s",
            type(err).__name__,
        )
        raise service_unavailable_exc from None
    except PyJWKSetError as err:
        logger.warning("Signing key not found in JWKS: %s", type(err).__name__)
        raise unauthorized_exc from None
    except (InvalidKeyError, PyJWKError) as err:
        logger.warning("Invalid or malformed JWK key encountered: %s", type(err).__name__)
        raise unauthorized_exc from None

    # Cryptographically decode and verify claims
    try:
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=settings.SUPABASE_JWT_ALGORITHMS,
            audience=settings.SUPABASE_JWT_AUDIENCE,
            issuer=settings.supabase_issuer,
            options={
                "require": ["exp", "iss", "aud", "sub"],
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": True,
            },
        )
    except InvalidTokenError as err:
        logger.debug("Asymmetric token verification rejected: %s", type(err).__name__)
        raise unauthorized_exc from None

    _validate_subject(payload.get("sub"), unauthorized_exc)
    return payload


def _validate_subject(sub: Any, exc: HTTPException) -> None:
    """Ensure subject claim exists and conforms to a valid UUID format."""
    if not sub or not isinstance(sub, str):
        raise exc
    try:
        UUID(sub)
    except (ValueError, TypeError):
        raise exc from None
