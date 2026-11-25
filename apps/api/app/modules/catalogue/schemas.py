"""Pydantic schemas for catalogue entities."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Money type (per TD-16)
class Money(BaseModel):
    amount: str = Field(..., description="Fixed-precision decimal string")
    currency: str = Field(..., description="ISO-4217 currency code")

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, v: str) -> str:
        return v.upper()

    @field_validator("currency")
    @classmethod
    def validate_currency_length(cls, v: str) -> str:
        if len(v) != 3:
            raise ValueError("Currency code must be 3 characters (ISO-4217)")
        return v


# Brand schemas
class BrandStatus(str, Enum):
    draft = "draft"
    active = "active"
    archived = "archived"


class BrandBase(BaseModel):
    slug: str = Field(..., min_length=1, max_length=120)
    name: str = Field(..., min_length=1, max_length=200)
    legal_name: Optional[str] = Field(None, max_length=200)
    status: BrandStatus = Field(default=BrandStatus.draft)

    @field_validator("slug")
    @classmethod
    def lowercase_slug(cls, v: str) -> str:
        return v.lower()


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    slug: Optional[str] = Field(None, min_length=1, max_length=120)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    legal_name: Optional[str] = Field(None, max_length=200)
    status: Optional[BrandStatus] = None
    logo_image_id: Optional[UUID] = None

    @field_validator("slug")
    @classmethod
    def lowercase_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.lower()
        return v


class BrandResponse(BrandBase):
    id: UUID
    logo_image_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Category schemas
class CategoryStatus(str, Enum):
    draft = "draft"
    active = "active"
    archived = "archived"


class CategoryBase(BaseModel):
    slug: str = Field(..., min_length=1, max_length=120)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    parent_id: Optional[UUID] = None
    sort_order: int = Field(default=0, ge=0)
    status: CategoryStatus = Field(default=CategoryStatus.draft)

    @field_validator("slug")
    @classmethod
    def lowercase_slug(cls, v: str) -> str:
        return v.lower()


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    slug: Optional[str] = Field(None, min_length=1, max_length=120)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    parent_id: Optional[UUID] = None
    sort_order: Optional[int] = Field(None, ge=0)
    status: Optional[CategoryStatus] = None

    @field_validator("slug")
    @classmethod
    def lowercase_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.lower()
        return v


class CategoryResponse(CategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Product status
class ProductStatus(str, Enum):
    draft = "draft"
    review = "review"
    published = "published"
    archived = "archived"


# Product schemas
class ProductBase(BaseModel):
    brand_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    model_number: Optional[str] = Field(None, max_length=120)
    source_model: Optional[str] = Field(None, max_length=200)
    name: str = Field(..., min_length=1, max_length=300)
    slug: str = Field(..., min_length=1, max_length=300)
    summary: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    source_description: Optional[str] = None
    status: ProductStatus = Field(default=ProductStatus.draft)
    publication_source: Optional[str] = Field(None, max_length=100)
    source_reference: Optional[str] = Field(None, max_length=200)
    catalogue_price: Optional[Money] = None
    tax_class: Optional[str] = Field(None, max_length=50)
    warranty_text: Optional[str] = Field(None, max_length=1000)

    @field_validator("slug")
    @classmethod
    def lowercase_slug(cls, v: str) -> str:
        return v.lower()


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    brand_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    model_number: Optional[str] = Field(None, max_length=120)
    source_model: Optional[str] = Field(None, max_length=200)
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    slug: Optional[str] = Field(None, min_length=1, max_length=300)
    summary: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    source_description: Optional[str] = None
    status: Optional[ProductStatus] = None
    publication_source: Optional[str] = Field(None, max_length=100)
    source_reference: Optional[str] = Field(None, max_length=200)
    catalogue_price: Optional[Money] = None
    tax_class: Optional[str] = Field(None, max_length=50)
    warranty_text: Optional[str] = Field(None, max_length=1000)

    @field_validator("slug")
    @classmethod
    def lowercase_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.lower()
        return v


class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int


# Product variant schemas
class VariantStatus(str, Enum):
    draft = "draft"
    active = "active"
    archived = "archived"


class ProductVariantBase(BaseModel):
    product_id: UUID
    sku: str = Field(..., min_length=1, max_length=120)
    name: Optional[str] = Field(None, max_length=200)
    option_values: Optional[dict[str, Any]] = None
    status: VariantStatus = Field(default=VariantStatus.draft)

    @field_validator("sku")
    @classmethod
    def uppercase_sku(cls, v: str) -> str:
        return v.upper()


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantUpdate(BaseModel):
    sku: Optional[str] = Field(None, min_length=1, max_length=120)
    name: Optional[str] = Field(None, max_length=200)
    option_values: Optional[dict[str, Any]] = None
    status: Optional[VariantStatus] = None

    @field_validator("sku")
    @classmethod
    def uppercase_sku(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.upper()
        return v


class ProductVariantResponse(ProductVariantBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Product image schemas
class ImageStatus(str, Enum):
    unverified = "unverified"
    verified = "verified"
    rejected = "rejected"


class ProductImageBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    storage_key: str = Field(..., min_length=1, max_length=500)
    alt_text: Optional[str] = Field(None, max_length=300)
    sort_order: int = Field(default=0, ge=0)
    width: Optional[int] = Field(None, ge=1)
    height: Optional[int] = Field(None, ge=1)
    checksum: Optional[str] = Field(None, max_length=64)
    source_url: Optional[str] = Field(None, max_length=1000)
    status: ImageStatus = Field(default=ImageStatus.unverified)


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageUpdate(BaseModel):
    alt_text: Optional[str] = Field(None, max_length=300)
    sort_order: Optional[int] = Field(None, ge=0)
    status: Optional[ImageStatus] = None


class ProductImageResponse(ProductImageBase):
    id: UUID
    verified_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Product attribute schemas
class ProductAttributeBase(BaseModel):
    product_id: UUID
    attribute_key: str = Field(..., min_length=1, max_length=120)
    attribute_value: str = Field(..., min_length=1, max_length=500)
    unit: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=100)
    confidence: Optional[str] = Field(None, max_length=50)

    @field_validator("attribute_key")
    @classmethod
    def lowercase_key(cls, v: str) -> str:
        return v.lower()


class ProductAttributeCreate(ProductAttributeBase):
    pass


class ProductAttributeUpdate(BaseModel):
    attribute_value: Optional[str] = Field(None, min_length=1, max_length=500)
    unit: Optional[str] = Field(None, max_length=50)
    confidence: Optional[str] = Field(None, max_length=50)


class ProductAttributeResponse(ProductAttributeBase):
    id: UUID
    verified_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Related product schemas
class RelationshipType(str, Enum):
    accessory = "accessory"
    compatible = "compatible"
    alternative = "alternative"
    upsell = "upsell"


class RelatedProductBase(BaseModel):
    product_id: UUID
    related_product_id: UUID
    relationship_type: RelationshipType
    sort_order: int = Field(default=0, ge=0)


class RelatedProductCreate(RelatedProductBase):
    pass


class RelatedProductResponse(RelatedProductBase):
    created_at: datetime

    model_config = {"from_attributes": True}


# Import batch schemas
class ImportStatus(str, Enum):
    pending = "pending"
    validating = "validating"
    validated = "validated"
    committed = "committed"
    failed = "failed"


class ImportBatchBase(BaseModel):
    source_filename: str = Field(..., min_length=1, max_length=500)
    source_hash: str = Field(..., min_length=1, max_length=64)
    total_rows: int = Field(..., ge=1)
    status: ImportStatus = Field(default=ImportStatus.pending)


class ImportBatchCreate(ImportBatchBase):
    pass


class ImportBatchResponse(ImportBatchBase):
    id: UUID
    valid_rows: int
    invalid_rows: int
    uploaded_by: UUID
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Import row result schemas
class RowStatus(str, Enum):
    pending = "pending"
    valid = "valid"
    invalid = "invalid"
    created = "created"
    error = "error"


class ImportRowResultBase(BaseModel):
    import_batch_id: UUID
    source_row_number: int = Field(..., ge=1)
    entity_type: Optional[str] = Field(None, max_length=50)
    external_key: Optional[str] = Field(None, max_length=200)
    status: RowStatus = Field(default=RowStatus.pending)
    errors: Optional[dict[str, Any]] = None


class ImportRowResultCreate(ImportRowResultBase):
    pass


class ImportRowResultResponse(ImportRowResultBase):
    id: UUID
    entity_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Publication request
class ProductPublishRequest(BaseModel):
    """Request to publish a product."""
    pass


class ProductPublishResponse(BaseModel):
    """Response after publication attempt."""
    product_id: UUID
    status: ProductStatus
    published_at: Optional[datetime] = None
    validation_errors: Optional[list[str]] = None
