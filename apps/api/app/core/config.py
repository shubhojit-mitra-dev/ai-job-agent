"""Application settings and environment configuration."""

from typing import Literal, Self

from pydantic import Field, model_validator
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
        default="dev-only-local-secret-key-not-for-production-min32b",
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
            "Connection pool class: 'NullPool' for serverless / transaction poolers (PgBouncer), "
            "or 'QueuePool' for stateful continuous local development connections."
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
        default="dev-only-placeholder-anon-key-local-dev",
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

    @model_validator(mode="after")
    def validate_production_configuration(self) -> Self:
        """Enforce strict configuration rules for production deployments."""
        if self.APP_ENV == "production":
            if "example.supabase.co" in self.SUPABASE_URL or not self.SUPABASE_URL.startswith(
                "https://"
            ):
                raise ValueError(
                    "SUPABASE_URL must be a valid https URL and cannot "
                    "use the example placeholder in production."
                )
            if (
                "dev-" in self.SUPABASE_ANON_KEY
                or "placeholder" in self.SUPABASE_ANON_KEY
                or len(self.SUPABASE_ANON_KEY) < 20
            ):
                raise ValueError(
                    "SUPABASE_ANON_KEY cannot use development placeholder "
                    "credentials in production."
                )
            if (
                "insecure" in self.APP_SECRET_KEY
                or "dev-" in self.APP_SECRET_KEY
                or len(self.APP_SECRET_KEY) < 32
            ):
                raise ValueError(
                    "APP_SECRET_KEY cannot use development placeholder and must "
                    "be at least 32 characters in production."
                )
            if self.SUPABASE_JWT_SECRET is not None:
                raise ValueError(
                    "SUPABASE_JWT_SECRET is forbidden in production; "
                    "asymmetric JWKS verification is strictly required."
                )
        return self

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
