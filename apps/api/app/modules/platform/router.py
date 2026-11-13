"""Admin/operations routes. Every route enforces permissions server-side."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.identity.deps import require_permission
from app.modules.identity.models import User
from app.modules.platform.models import AuditLog

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/audit-logs")
async def list_audit_logs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(require_permission("audit.read")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Paginated audit log search. Requires the audit.read permission."""
    total = (await session.execute(select(func.count(AuditLog.id)))).scalar_one()
    result = await session.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
    )
    return {
        "items": [
            {
                "id": str(row.id),
                "actor_user_id": str(row.actor_user_id) if row.actor_user_id else None,
                "action": row.action,
                "entity_type": row.entity_type,
                "entity_id": row.entity_id,
                "correlation_id": row.correlation_id,
                "created_at": row.created_at.isoformat(),
            }
            for row in result.scalars().all()
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
