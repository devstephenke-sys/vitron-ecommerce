"""SQLAlchemy ORM models for catalogue entities."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Brand(Base):
    """Brand model."""

    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    logo_image_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("draft", "active", "archived", name="brandstatus", native_enum=False, length=20),
        server_default="draft",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    __table_args__ = (
        CheckConstraint("slug = lower(slug)", name="ck_brands_slug_normalized"),
        UniqueConstraint("slug", name="uq_brands_slug"),
        Index("ix_brands_status", "status"),
    )

    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="brand", lazy="selectin"
    )


class Category(Base):
    """Category model with hierarchical support."""

    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=True
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("draft", "active", "archived", name="categorystatus", native_enum=False, length=20),
        server_default="draft",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    __table_args__ = (
        CheckConstraint("slug = lower(slug)", name="ck_categories_slug_normalized"),
        UniqueConstraint("slug", name="uq_categories_slug"),
        Index("ix_categories_parent_id", "parent_id"),
        Index("ix_categories_status", "status"),
    )

    parent: Mapped["Category | None"] = relationship(
        "Category", remote_side=[id], back_populates="children", lazy="selectin"
    )
    children: Mapped[list["Category"]] = relationship(
        "Category", back_populates="parent", lazy="selectin"
    )
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="category", lazy="selectin"
    )


class Product(Base):
    """Product model with source data preservation (BD-05)."""

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="SET NULL"), nullable=True
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    model_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_model: Mapped[str | None] = mapped_column(String(200), nullable=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), nullable=False)
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("draft", "review", "published", "archived", name="productstatus", native_enum=False, length=20),
        server_default="draft",
        nullable=False,
    )
    publication_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    catalogue_price_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency_code: Mapped[str | None] = mapped_column(String(3), nullable=True)
    tax_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    warranty_text: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("slug = lower(slug)", name="ck_products_slug_normalized"),
        CheckConstraint("char_length(currency_code) = 3", name="ck_products_currency_len"),
        CheckConstraint("currency_code = upper(currency_code)", name="ck_products_currency_upper"),
        UniqueConstraint("slug", name="uq_products_slug"),
        Index("ix_products_brand_id", "brand_id"),
        Index("ix_products_category_id", "category_id"),
        Index("ix_products_model_number", "model_number"),
        Index("ix_products_status", "status"),
        Index("ix_products_name_search", "name"),
    )

    brand: Mapped["Brand | None"] = relationship("Brand", back_populates="products", lazy="selectin")
    category: Mapped["Category | None"] = relationship("Category", back_populates="products", lazy="selectin")
    variants: Mapped[list["ProductVariant"]] = relationship(
        "ProductVariant", back_populates="product", lazy="selectin", cascade="all, delete-orphan"
    )
    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage", back_populates="product", lazy="selectin", cascade="all, delete-orphan"
    )
    attributes: Mapped[list["ProductAttribute"]] = relationship(
        "ProductAttribute", back_populates="product", lazy="selectin", cascade="all, delete-orphan"
    )
    related_as_product: Mapped[list["RelatedProduct"]] = relationship(
        "RelatedProduct", foreign_keys="RelatedProduct.product_id", back_populates="product", lazy="selectin", cascade="all, delete-orphan"
    )
    related_as_related: Mapped[list["RelatedProduct"]] = relationship(
        "RelatedProduct", foreign_keys="RelatedProduct.related_product_id", back_populates="related_product", lazy="selectin", cascade="all, delete-orphan"
    )


class ProductVariant(Base):
    """Product variant model (one default variant per product initially)."""

    __tablename__ = "product_variants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    sku: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    option_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("draft", "active", "archived", name="variantstatus", native_enum=False, length=20),
        server_default="draft",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    __table_args__ = (
        CheckConstraint("sku = upper(sku)", name="ck_product_variants_sku_upper"),
        UniqueConstraint("sku", name="uq_product_variants_sku"),
        Index("ix_product_variants_product_id", "product_id"),
        Index("ix_product_variants_status", "status"),
    )

    product: Mapped["Product"] = relationship("Product", back_populates="variants", lazy="selectin")
    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage", back_populates="variant", lazy="selectin", cascade="all, delete-orphan"
    )


class ProductImage(Base):
    """Product image model with unverified status (BD-10)."""

    __tablename__ = "product_images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True
    )
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(300), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("unverified", "verified", "rejected", name="imagestatus", native_enum=False, length=20),
        server_default="unverified",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    __table_args__ = (
        Index("ix_product_images_product_id", "product_id"),
        Index("ix_product_images_variant_id", "variant_id"),
        Index("ix_product_images_status", "status"),
    )

    product: Mapped["Product"] = relationship("Product", back_populates="images", lazy="selectin")
    variant: Mapped["ProductVariant | None"] = relationship("ProductVariant", back_populates="images", lazy="selectin")


class ProductAttribute(Base):
    """Product attribute model with source tracking."""

    __tablename__ = "product_attributes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    attribute_key: Mapped[str] = mapped_column(String(120), nullable=False)
    attribute_value: Mapped[str] = mapped_column(String(500), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(50), nullable=True)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    __table_args__ = (
        CheckConstraint("attribute_key = lower(attribute_key)", name="ck_product_attributes_key_normalized"),
        Index("ix_product_attributes_product_id", "product_id"),
        Index("ix_product_attributes_key_value", "attribute_key", "attribute_value"),
    )

    product: Mapped["Product"] = relationship("Product", back_populates="attributes", lazy="selectin")


class RelatedProduct(Base):
    """Related products with relationship types."""

    __tablename__ = "related_products"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), primary_key=True
    )
    related_product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), primary_key=True
    )
    relationship_type: Mapped[str] = mapped_column(
        Enum("accessory", "compatible", "alternative", "upsell", name="relationshiptype", native_enum=False, length=20),
        primary_key=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    __table_args__ = (
        Index("ix_related_products_related", "related_product_id"),
    )

    product: Mapped["Product"] = relationship("Product", foreign_keys=[product_id], back_populates="related_as_product", lazy="selectin")
    related_product: Mapped["Product"] = relationship("Product", foreign_keys=[related_product_id], back_populates="related_as_related", lazy="selectin")


class ImportBatch(Base):
    """Import batch model for catalogue imports."""

    __tablename__ = "import_batches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    source_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("pending", "validating", "validated", "committed", "failed", name="importstatus", native_enum=False, length=20),
        server_default="pending",
        nullable=False,
    )
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    valid_rows: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    invalid_rows: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_import_batches_status", "status"),
        Index("ix_import_batches_uploaded_by", "uploaded_by"),
    )

    row_results: Mapped[list["ImportRowResult"]] = relationship(
        "ImportRowResult", back_populates="import_batch", lazy="selectin", cascade="all, delete-orphan"
    )


class ImportRowResult(Base):
    """Import row result model for tracking individual row outcomes."""

    __tablename__ = "import_row_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    import_batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("import_batches.id", ondelete="CASCADE"), nullable=False
    )
    source_row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    external_key: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("pending", "valid", "invalid", "created", "error", name="rowstatus", native_enum=False, length=20),
        server_default="pending",
        nullable=False,
    )
    errors: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    __table_args__ = (
        Index("ix_import_row_results_batch_id", "import_batch_id"),
        Index("ix_import_row_results_entity", "entity_type", "entity_id"),
        Index("ix_import_row_results_status", "status"),
    )

    import_batch: Mapped["ImportBatch"] = relationship("ImportBatch", back_populates="row_results", lazy="selectin")
