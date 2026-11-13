"""Customer account ORM models: addresses and customer_profiles."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    recipient_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    line1: Mapped[str] = mapped_column(String(300), nullable=False)
    line2: Mapped[str | None] = mapped_column(String(300), nullable=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="KE")
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("country_code = upper(country_code)", name="ck_addresses_country_upper"),
        CheckConstraint("char_length(country_code) = 2", name="ck_addresses_country_len"),
    )


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    preferred_contact_method: Mapped[str | None] = mapped_column(String(32), nullable=True)
    marketing_opt_in: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
