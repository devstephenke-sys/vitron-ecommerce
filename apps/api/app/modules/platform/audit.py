"""Audit logging helpers.

Audit records are append-only: this module exposes write and read
helpers only — there are intentionally no update/delete functions.
IP addresses and user agents are stored as SHA-256 hashes, never raw.
"""

import hashlib
import uuid

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import request_id_var
from app.modules.platform.models import AuditLog


def _sha256(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def request_hashes(request: Request | None) -> tuple[str | None, str | None]:
    if request is None:
        return None, None
    ip = request.client.host if request.client else None
    return _sha256(ip), _sha256(request.headers.get("user-agent"))


async def record_audit(
    session: AsyncSession,
    *,
    action: str,
    entity_type: str,
    entity_id: str | uuid.UUID | None = None,
    actor_user_id: uuid.UUID | None = None,
    before: dict | None = None,
    after: dict | None = None,
    request: Request | None = None,
) -> AuditLog:
    ip_hash, ua_hash = request_hashes(request)
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        before_=before,
        after_=after,
        ip_hash=ip_hash,
        user_agent_hash=ua_hash,
        correlation_id=request_id_var.get() if request_id_var.get() != "-" else None,
    )
    session.add(entry)
    return entry
