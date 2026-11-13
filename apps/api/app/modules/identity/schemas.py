"""Pydantic request/response schemas for the identity module."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    display_name: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=32)

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    # When provided, only that token's family is revoked; when omitted,
    # all of the user's refresh-token families are revoked (sign out all).
    refresh_token: str | None = Field(default=None, min_length=1)


class PasswordResetRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    display_name: str | None
    phone: str | None
    status: str
    email_verified: bool
    created_at: datetime

    @classmethod
    def from_user(cls, user: "User") -> "UserOut":  # noqa: F821
        return cls(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            phone=user.phone,
            status=user.status.value if hasattr(user.status, "value") else str(user.status),
            email_verified=user.email_verified_at is not None,
            created_at=user.created_at,
        )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105
    expires_in: int
    refresh_token: str
    user: UserOut
    permissions: list[str]


class MeResponse(BaseModel):
    user: UserOut
    permissions: list[str]


class UpdateMeRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=32)


class AddressIn(BaseModel):
    recipient_name: str = Field(min_length=1, max_length=200)
    phone: str = Field(min_length=1, max_length=32)
    line1: str = Field(min_length=1, max_length=300)
    line2: str | None = Field(default=None, max_length=300)
    city: str = Field(min_length=1, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    country_code: str = Field(default="KE", min_length=2, max_length=2)
    postal_code: str | None = Field(default=None, max_length=20)
    is_default: bool = False

    @field_validator("country_code")
    @classmethod
    def _upper_country(cls, v: str) -> str:
        return v.upper()


class AddressUpdate(BaseModel):
    recipient_name: str | None = Field(default=None, min_length=1, max_length=200)
    phone: str | None = Field(default=None, min_length=1, max_length=32)
    line1: str | None = Field(default=None, min_length=1, max_length=300)
    line2: str | None = Field(default=None, max_length=300)
    city: str | None = Field(default=None, min_length=1, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    postal_code: str | None = Field(default=None, max_length=20)
    is_default: bool | None = None

    @field_validator("country_code")
    @classmethod
    def _upper_country(cls, v: str | None) -> str | None:
        return v.upper() if v else v


class AddressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recipient_name: str
    phone: str
    line1: str
    line2: str | None
    city: str
    region: str | None
    country_code: str
    postal_code: str | None
    is_default: bool
    created_at: datetime
