"""API v1 root router assembling all domain modules."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
