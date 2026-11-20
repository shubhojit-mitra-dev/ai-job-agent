"""FastAPI authentication dependencies."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import verify_supabase_jwt
from app.modules.auth.schemas import CurrentUser

bearer_scheme = HTTPBearer(
    auto_error=True,
    description="Supabase Auth JWT bearer token",
)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> CurrentUser:
    """Dependency extracting and validating authenticated CurrentUser from Bearer token."""
    payload = verify_supabase_jwt(credentials.credentials)
    raw_email = payload.get("email")
    role = str(payload.get("role", "authenticated"))

    return CurrentUser(
        user_id=UUID(str(payload["sub"])),
        email=raw_email if raw_email else None,
        role=role,
    )
