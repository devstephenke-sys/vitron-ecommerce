"""Aggregate versioned API routers."""

from fastapi import APIRouter

from app.api.v1 import health
from app.modules.catalogue.public import router as public_catalog_router
from app.modules.catalogue.router import router as catalogue_router
from app.modules.identity.router import router as identity_router
from app.modules.platform.router import router as platform_router

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(identity_router)
api_router.include_router(platform_router)
api_router.include_router(catalogue_router)
api_router.include_router(public_catalog_router)
