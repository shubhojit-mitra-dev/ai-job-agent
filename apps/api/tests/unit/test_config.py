"""Unit tests for configuration validation across development and production modes."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_development_configuration_accepts_defaults() -> None:
    """Verify local development mode accepts local defaults."""
    settings = Settings(APP_ENV="development")
    assert settings.APP_ENV == "development"
    assert settings.DB_POOL_CLASS == "NullPool"
    assert settings.DB_STATEMENT_CACHE_SIZE == 0
    assert "supabase.co" in settings.SUPABASE_URL


def test_production_rejects_example_supabase_url() -> None:
    """Verify production rejects example placeholder Supabase URL."""
    with pytest.raises(ValidationError, match="SUPABASE_URL must be a valid https URL"):
        Settings(
            APP_ENV="production",
            SUPABASE_URL="https://example.supabase.co",
            SUPABASE_ANON_KEY="valid-length-anon-key-with-no-dev-prefix-12345",
            APP_SECRET_KEY="production-super-strong-secret-key-at-least-32b",
        )


def test_production_rejects_dev_anon_key() -> None:
    """Verify production rejects development placeholder anon key."""
    with pytest.raises(
        ValidationError,
        match="SUPABASE_ANON_KEY cannot use development placeholder",
    ):
        Settings(
            APP_ENV="production",
            SUPABASE_URL="https://prod-project.supabase.co",
            SUPABASE_ANON_KEY="dev-placeholder-anon-key",
            APP_SECRET_KEY="production-super-strong-secret-key-at-least-32b",
        )


def test_production_rejects_insecure_app_secret() -> None:
    """Verify production rejects insecure application secret keys."""
    with pytest.raises(ValidationError, match="APP_SECRET_KEY cannot use development placeholder"):
        Settings(
            APP_ENV="production",
            SUPABASE_URL="https://prod-project.supabase.co",
            SUPABASE_ANON_KEY="prod-anon-key-that-is-long-enough-for-validation",
            APP_SECRET_KEY="insecure-dev-secret-key-too-short",
        )


def test_production_rejects_jwt_secret_fallback() -> None:
    """Verify production strictly forbids shared symmetric JWT secret."""
    with pytest.raises(ValidationError, match="SUPABASE_JWT_SECRET is forbidden in production"):
        Settings(
            APP_ENV="production",
            SUPABASE_URL="https://prod-project.supabase.co",
            SUPABASE_ANON_KEY="prod-anon-key-that-is-long-enough-for-validation",
            APP_SECRET_KEY="production-super-strong-secret-key-at-least-32b",
            SUPABASE_JWT_SECRET="some-symmetric-secret",
        )


def test_production_accepts_valid_configuration() -> None:
    """Verify production mode accepts valid, secure configuration."""
    settings = Settings(
        APP_ENV="production",
        SUPABASE_URL="https://my-real-app.supabase.co",
        SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real-anon-payload-string",
        APP_SECRET_KEY="a-very-secure-32-byte-secret-key-for-production-use",
        SUPABASE_JWT_SECRET=None,
    )
    assert settings.APP_ENV == "production"
    assert settings.supabase_issuer == "https://my-real-app.supabase.co/auth/v1"
