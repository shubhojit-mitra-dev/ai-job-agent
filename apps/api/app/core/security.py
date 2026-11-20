"""Cryptographic token verification and security utilities."""

from typing import Any
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient, PyJWTError

from app.core.config import settings

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
    """
    unauthorized_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token or not isinstance(token, str):
        raise unauthorized_exc

    # Non-production test fallback strictly forbidden in production
    if settings.APP_ENV != "production" and settings.SUPABASE_JWT_SECRET is not None:
        try:
            # Check if token is HS256 signed for local mock test convenience
            header = jwt.get_unverified_header(token)
            if header.get("alg") == "HS256":
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
        except PyJWTError:
            raise unauthorized_exc from None

    # Authoritative Production Path: Asymmetric JWKS verification
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg")
        if alg not in settings.SUPABASE_JWT_ALGORITHMS:
            raise unauthorized_exc

        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

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
        _validate_subject(payload.get("sub"), unauthorized_exc)
        return payload
    except (PyJWTError, Exception):
        raise unauthorized_exc from None


def _validate_subject(sub: Any, exc: HTTPException) -> None:
    """Ensure subject claim exists and conforms to a valid UUID format."""
    if not sub or not isinstance(sub, str):
        raise exc
    try:
        UUID(sub)
    except (ValueError, TypeError):
        raise exc from None
