"""Identity HTTP routes: /auth/* and /me*.

Public auth endpoints are rate-limited per client IP. Authorization for
protected routes is enforced here by FastAPI dependencies — never by the
frontend.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ratelimit import rate_limit
from app.db.session import get_db_session
from app.modules.accounts.models import Address
from app.modules.identity import service
from app.modules.identity.deps import get_current_user
from app.modules.identity.models import User
from app.modules.identity.schemas import (
    AddressIn,
    AddressOut,
    AddressUpdate,
    LoginRequest,
    LogoutRequest,
    MeResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UpdateMeRequest,
    UserOut,
)

router = APIRouter(tags=["auth"])

RL_REGISTER = Depends(rate_limit("auth.register", limit=10, window_seconds=60))
RL_LOGIN = Depends(rate_limit("auth.login", limit=10, window_seconds=60))
RL_REFRESH = Depends(rate_limit("auth.refresh", limit=30, window_seconds=60))
RL_RESET_REQUEST = Depends(rate_limit("auth.reset.request", limit=5, window_seconds=60))
RL_RESET_CONFIRM = Depends(rate_limit("auth.reset.confirm", limit=10, window_seconds=60))


# ---------------------------------------------------------------- auth


@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _rate: None = RL_REGISTER,
) -> TokenResponse:
    return await service.register(session, payload, request)


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _rate: None = RL_LOGIN,
) -> TokenResponse:
    return await service.authenticate(session, payload, request)


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _rate: None = RL_REFRESH,
) -> TokenResponse:
    return await service.rotate_refresh_token(session, payload.refresh_token, request)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: LogoutRequest,
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    await service.revoke_session(session, user, payload.refresh_token, request)


@router.post("/auth/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
async def password_reset_request(
    payload: PasswordResetRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _rate: None = RL_RESET_REQUEST,
) -> dict:
    # Always the same response — never reveal whether the account exists.
    await service.request_password_reset(session, payload.email, request)
    return {"status": "accepted"}


@router.post("/auth/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def password_reset_confirm(
    payload: PasswordResetConfirm,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _rate: None = RL_RESET_CONFIRM,
) -> None:
    await service.confirm_password_reset(session, payload, request)


# ------------------------------------------------------------------ me


@router.get("/me", response_model=MeResponse)
async def read_me(user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        user=UserOut.from_user(user),
        permissions=service.user_permission_codes(user),
    )


@router.patch("/me", response_model=MeResponse)
async def update_me(
    payload: UpdateMeRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> MeResponse:
    if payload.display_name is not None:
        user.display_name = payload.display_name
    if payload.phone is not None:
        user.phone = payload.phone or None
    await session.flush()
    return MeResponse(
        user=UserOut.from_user(user),
        permissions=service.user_permission_codes(user),
    )


# ------------------------------------------------------------- addresses


@router.get("/me/addresses", response_model=list[AddressOut])
async def list_addresses(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[Address]:
    result = await session.execute(
        select(Address).where(Address.user_id == user.id).order_by(Address.created_at)
    )
    return list(result.scalars().all())


@router.post(
    "/me/addresses",
    response_model=AddressOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_address(
    payload: AddressIn,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Address:
    if payload.is_default:
        await _clear_default(session, user.id)
    address = Address(user_id=user.id, **payload.model_dump())
    session.add(address)
    await session.flush()
    return address


@router.patch("/me/addresses/{address_id}", response_model=AddressOut)
async def update_address(
    address_id: uuid.UUID,
    payload: AddressUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Address:
    address = await _get_owned_address(session, address_id, user.id)
    changes = payload.model_dump(exclude_unset=True)
    if changes.get("is_default"):
        await _clear_default(session, user.id, exclude_id=address.id)
    for field, value in changes.items():
        setattr(address, field, value)
    await session.flush()
    return address


@router.delete("/me/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    address = await _get_owned_address(session, address_id, user.id)
    await session.delete(address)


async def _get_owned_address(
    session: AsyncSession, address_id: uuid.UUID, user_id: uuid.UUID
) -> Address:
    result = await session.execute(
        select(Address).where(Address.id == address_id, Address.user_id == user_id)
    )
    address = result.scalar_one_or_none()
    if address is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return address


async def _clear_default(
    session: AsyncSession, user_id: uuid.UUID, exclude_id: uuid.UUID | None = None
) -> None:
    stmt = select(Address).where(Address.user_id == user_id, Address.is_default.is_(True))
    if exclude_id is not None:
        stmt = stmt.where(Address.id != exclude_id)
    result = await session.execute(stmt)
    for existing in result.scalars().all():
        existing.is_default = False
