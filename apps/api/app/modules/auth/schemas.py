"""Authentication schemas and identity models."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CurrentUser(BaseModel):
    """Authenticated user context extracted from verified JWT."""

    model_config = ConfigDict(frozen=True)

    user_id: UUID = Field(
        ...,
        description="Unique candidate identifier (sub claim)",
    )
    email: EmailStr | None = Field(
        default=None,
        description="Candidate email address if present in claims",
    )
    role: str = Field(
        default="authenticated",
        description="Supabase Auth role claim. Not to be used as authorization without validation.",
    )
