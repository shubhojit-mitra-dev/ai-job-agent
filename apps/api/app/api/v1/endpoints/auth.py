"""Authentication and identity endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import CurrentUser

router = APIRouter()


@router.get(
    "/me",
    response_model=CurrentUser,
    summary="Get current authenticated candidate",
    description="Returns identity and verified claims of currently authenticated candidate.",
)
async def get_me(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    """Return the currently authenticated candidate."""
    return current_user
