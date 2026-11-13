"""Health check endpoints.

- ``/live``  — process is running (liveness probe).
- ``/ready`` — required dependencies (currently PostgreSQL) are reachable
  (readiness probe). Never exposes connection strings or credentials.
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def liveness() -> dict:
    """Liveness probe: the application process is up."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Readiness probe: verify database connectivity with a trivial query."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        # Do not leak driver/connection details to callers.
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "database": "unavailable"}
    return {"status": "ready", "database": "ok"}
