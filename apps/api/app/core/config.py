"""Application settings and environment configuration."""

from typing import Literal

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application settings loaded from environment and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: Literal["development", "test", "production"] = "development"
    APP_SECRET_KEY: str = Field(
        default="insecure-dev-secret-key-change-in-production-32b",
        description="Application secret key for local cryptographic state",
    )

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/career_platform",
        description="Async database connection URL used by application runtime",
    )
    MIGRATION_DATABASE_URL: str | None = Field(
        default=None,
        description=(
            "Direct session-mode database URL (port 5432) for Alembic migrations. "
            "Defaults to DATABASE_URL if unset."
        ),
    )
    DB_POOL_CLASS: Literal["NullPool", "QueuePool"] = Field(
        default="NullPool",
        description=(
            "NullPool for serverless / transaction pooler; QueuePool for continuous local dev."
        ),
    )
    DB_STATEMENT_CACHE_SIZE: int = Field(
        default=0,
        description=(
            "Must remain 0 for Supabase / PgBouncer transaction pooling "
            "to prevent prepared-statement failures."
        ),
    )

    # Supabase Authentication & Cryptographic Verification
    SUPABASE_URL: str = Field(
        default="https://example.supabase.co",
        description="Supabase project URL",
    )
    SUPABASE_ANON_KEY: str = Field(
        default="dev-anon-key",
        description="Supabase anonymous client key",
    )
    SUPABASE_JWT_AUDIENCE: str = Field(
        default="authenticated",
        description="Audience claim ('aud') required on incoming Supabase access tokens",
    )
    SUPABASE_JWT_ALGORITHMS: list[str] = Field(
        default=["RS256", "ES256"],
        description="Allowed asymmetric signature algorithms for Supabase JWKS verification",
    )
    SUPABASE_JWT_SECRET: str | None = Field(
        default=None,
        description="Optional shared secret for test environments only. Forbidden in production.",
    )

    @field_validator("SUPABASE_JWT_SECRET")
    @classmethod
    def validate_jwt_secret_in_prod(cls, v: str | None, info: ValidationInfo) -> str | None:
        app_env = info.data.get("APP_ENV", "development")
        if app_env == "production" and v is not None:
            raise ValueError(
                "SUPABASE_JWT_SECRET is forbidden in production; "
                "asymmetric JWKS verification is strictly required."
            )
        return v

    @property
    def supabase_issuer(self) -> str:
        """Derived authoritative Supabase Auth token issuer."""
        return f"{self.SUPABASE_URL.rstrip('/')}/auth/v1"

    @property
    def supabase_jwks_url(self) -> str:
        """Authoritative endpoint for Supabase public JSON Web Key Set (JWKS)."""
        return f"{self.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"

    @property
    def migration_url(self) -> str:
        """Resolved migration database connection URL."""
        return self.MIGRATION_DATABASE_URL or self.DATABASE_URL


settings = Settings()
