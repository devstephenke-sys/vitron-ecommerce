"""Aggregate versioned API routers."""

from fastapi import APIRouter

from app.api.v1 import health
from app.modules.identity.router import router as identity_router
from app.modules.platform.router import router as platform_router

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(identity_router)
api_router.include_router(platform_router)
