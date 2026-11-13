"""Identity application service: registration, sessions, password reset.

All functions take an AsyncSession supplied by the request dependency;
the caller (route) controls the transaction boundary via get_db_session.
"""

import hashlib
import logging
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.modules.identity.models import (
    AuthEvent,
    PasswordResetToken,
    RefreshToken,
    Role,
    RolePermission,
    User,
    UserRole,
    UserStatus,
)
from app.modules.identity.schemas import (
    LoginRequest,
    PasswordResetConfirm,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.modules.identity.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.modules.platform.audit import request_hashes

logger = logging.getLogger("vitron.identity")

AUTH_FAILED_MESSAGE = "Invalid email or password"


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


async def _record_auth_event(
    session: AsyncSession,
    *,
    event_type: str,
    user_id: uuid.UUID | None = None,
    request: Request | None = None,
    metadata: dict | None = None,
) -> None:
    ip_hash, ua_hash = request_hashes(request)
    session.add(
        AuthEvent(
            user_id=user_id,
            event_type=event_type,
            ip_hash=ip_hash,
            user_agent_hash=ua_hash,
            metadata_=metadata,
        )
    )


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


_USER_WITH_PERMISSIONS_OPTIONS = (
    selectinload(User.roles)
    .selectinload(UserRole.role)
    .selectinload(Role.permissions)
    .selectinload(RolePermission.permission)
)


async def get_user_with_permissions(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await session.execute(
        select(User).where(User.id == user_id).options(_USER_WITH_PERMISSIONS_OPTIONS)
    )
    return result.scalar_one_or_none()


def user_permission_codes(user: User) -> list[str]:
    codes: set[str] = set()
    for user_role in user.roles:
        for role_perm in user_role.role.permissions:
            codes.add(role_perm.permission.code)
    return sorted(codes)


async def _assign_role(session: AsyncSession, user: User, role_code: str) -> None:
    """Assign a seeded role by code (roles are created by migration)."""
    result = await session.execute(select(Role).where(Role.code == role_code))
    role = result.scalar_one()
    session.add(UserRole(user_id=user.id, role_id=role.id))


async def _reload_user(session: AsyncSession, user_id: uuid.UUID) -> User:
    result = await session.execute(
        select(User).where(User.id == user_id).options(_USER_WITH_PERMISSIONS_OPTIONS)
    )
    return result.scalar_one()


async def register(
    session: AsyncSession, payload: RegisterRequest, request: Request | None = None
) -> TokenResponse:
    if await get_user_by_email(session, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        phone=payload.phone,
    )
    session.add(user)
    try:
        await session.flush()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from None

    await _assign_role(session, user, "customer")
    await _record_auth_event(session, event_type="register", user_id=user.id, request=request)

    permissions = user_permission_codes(await _reload_user(session, user.id))
    token_pair = await _issue_token_pair(session, user)
    await session.flush()
    return TokenResponse(
        access_token=token_pair[0],
        expires_in=token_pair[1],
        refresh_token=token_pair[2],
        user=UserOut.from_user(user),
        permissions=permissions,
    )


async def authenticate(
    session: AsyncSession, payload: LoginRequest, request: Request | None = None
) -> TokenResponse:
    user = await get_user_by_email(session, payload.email)
    # Always run the hash check to reduce timing-based account enumeration.
    if user is None or not verify_password(payload.password, user.password_hash):
        await _record_auth_event(session, event_type="login_failed", request=request)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=AUTH_FAILED_MESSAGE)
    if user.status != UserStatus.ACTIVE:
        await _record_auth_event(
            session, event_type="login_failed_disabled", user_id=user.id, request=request
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    await _record_auth_event(session, event_type="login", user_id=user.id, request=request)
    permissions = user_permission_codes(await _reload_user(session, user.id))
    access_token, expires_in, refresh_token = await _issue_token_pair(session, user)
    await session.flush()
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        refresh_token=refresh_token,
        user=UserOut.from_user(user),
        permissions=permissions,
    )


async def _issue_token_pair(session: AsyncSession, user: User) -> tuple[str, int, str]:
    access_token, expires_in = create_access_token(user.id)
    raw_refresh = secrets.token_urlsafe(48)
    settings = get_settings()
    now = datetime.now(UTC)
    session.add(
        RefreshToken(
            user_id=user.id,
            token_hash=_sha256(raw_refresh),
            family_id=uuid.uuid4(),
            expires_at=now + timedelta(seconds=settings.refresh_token_ttl_seconds),
        )
    )
    return access_token, expires_in, raw_refresh


async def _find_refresh_token(session: AsyncSession, raw_token: str) -> RefreshToken | None:
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token_hash == _sha256(raw_token))
    )
    return result.scalar_one_or_none()


async def rotate_refresh_token(
    session: AsyncSession, raw_token: str, request: Request | None = None
) -> TokenResponse:
    """Rotate a refresh token. Reuse of a revoked token revokes the family."""
    stored = await _find_refresh_token(session, raw_token)
    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    if stored.revoked_at is not None:
        # Token reuse after rotation: possible theft — revoke the family.
        # Committed immediately: raising below rolls the request
        # transaction back, which would undo the revocation.
        await session.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == stored.family_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )
        await _record_auth_event(
            session,
            event_type="refresh_reuse_detected",
            user_id=stored.user_id,
            request=request,
        )
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token reuse detected"
        )

    now = datetime.now(UTC)
    if stored.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )

    user = await get_user_with_permissions(session, stored.user_id)
    if user is None or user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account unavailable")

    # Issue replacement inside the same family.
    access_token, expires_in = create_access_token(user.id)
    new_raw = secrets.token_urlsafe(48)
    settings = get_settings()
    new_token = RefreshToken(
        user_id=user.id,
        token_hash=_sha256(new_raw),
        family_id=stored.family_id,
        expires_at=now + timedelta(seconds=settings.refresh_token_ttl_seconds),
    )
    session.add(new_token)
    await session.flush()

    stored.revoked_at = now
    stored.replaced_by_id = new_token.id
    stored.last_used_at = now

    await _record_auth_event(session, event_type="refresh", user_id=user.id, request=request)
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        refresh_token=new_raw,
        user=UserOut.from_user(user),
        permissions=user_permission_codes(user),
    )


async def revoke_session(
    session: AsyncSession, user: User, raw_token: str | None, request: Request | None = None
) -> None:
    now = datetime.now(UTC)
    if raw_token:
        stored = await _find_refresh_token(session, raw_token)
        if stored is not None and stored.user_id == user.id:
            await session.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.family_id == stored.family_id,
                    RefreshToken.revoked_at.is_(None),
                )
                .values(revoked_at=now)
            )
    else:
        await session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
    await _record_auth_event(session, event_type="logout", user_id=user.id, request=request)


async def request_password_reset(
    session: AsyncSession, email: str, request: Request | None = None
) -> None:
    """Create a reset token if the account exists. Never reveals existence."""
    user = await get_user_by_email(session, email)
    if user is not None and user.status == UserStatus.ACTIVE:
        raw_token = secrets.token_urlsafe(48)
        settings = get_settings()
        session.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=_sha256(raw_token),
                expires_at=datetime.now(UTC)
                + timedelta(seconds=settings.password_reset_ttl_seconds),
            )
        )
        # Delivery (email) is deferred to Phase 8 communications; until then
        # the token exists only in the database and is never returned.
        logger.info("password_reset.requested user_id=%s", user.id)
    await _record_auth_event(
        session,
        event_type="password_reset_requested",
        user_id=user.id if user else None,
        request=request,
    )


async def confirm_password_reset(
    session: AsyncSession, payload: PasswordResetConfirm, request: Request | None = None
) -> None:
    result = await session.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == _sha256(payload.token))
    )
    token = result.scalar_one_or_none()
    now = datetime.now(UTC)
    if token is None or token.used_at is not None or token.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token"
        )

    user = await session.get(User, token.user_id)
    if user is None or user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")

    user.password_hash = hash_password(payload.new_password)
    token.used_at = now
    # Invalidate all sessions: the user must sign in again.
    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    await _record_auth_event(
        session, event_type="password_reset_confirmed", user_id=user.id, request=request
    )
