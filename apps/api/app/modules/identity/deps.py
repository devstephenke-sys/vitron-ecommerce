"""FastAPI dependencies for authentication and authorization.

Security model: the admin frontend route guard is UX only. Every
protected operation re-authenticates the Bearer JWT and re-checks the
caller's permissions against the database on each request — role or
permission changes take effect immediately.
"""

from collections.abc import Awaitable, Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.identity import service
from app.modules.identity.models import User, UserStatus
from app.modules.identity.security import decode_access_token

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """Resolve the Bearer access token to an active user with permissions."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await service.get_user_with_permissions(session, user_id)
    if user is None or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account unavailable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_permission(permission: str) -> Callable[..., Awaitable[User]]:
    """Dependency factory: caller must hold `permission` (checked in DB)."""

    async def _check(user: User = Depends(get_current_user)) -> User:
        if permission not in service.user_permission_codes(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _check


def require_any_permission(*permissions: str) -> Callable[..., Awaitable[User]]:
    """Dependency factory: caller must hold at least one of `permissions`."""

    async def _check(user: User = Depends(get_current_user)) -> User:
        held = set(service.user_permission_codes(user))
        if not held.intersection(permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _check


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"
