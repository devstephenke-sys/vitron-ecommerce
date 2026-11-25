"""Public catalog router - read-only, published products only."""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, or_

from app.db.session import get_db_session
from app.modules.catalogue.models import Brand, Category, Product
from app.modules.catalogue.schemas import (
    BrandResponse,
    CategoryResponse,
)

router = APIRouter(prefix="/catalog", tags=["public-catalog"])


# Public schemas that exclude internal fields
class PublicProductResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    summary: Optional[str] = None
    description: Optional[str] = None
    catalogue_price: Optional[dict] = None
    currency_code: Optional[str] = None
    brand: Optional[BrandResponse] = None
    category: Optional[CategoryResponse] = None

    model_config = {"from_attributes": True}


class PublicProductListResponse(BaseModel):
    items: list[PublicProductResponse]
    total: int
    page: int
    page_size: int


@router.get("/products", response_model=PublicProductListResponse)
async def list_public_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    brand: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db_session),
):
    """List published products with filtering and pagination."""
    # Only return published products
    query = (
        select(Product)
        .options(selectinload(Product.brand), selectinload(Product.category))
        .where(Product.status == "published")
    )

    # Filter by brand slug
    if brand:
        query = query.join(Brand).where(Brand.slug == brand.lower())

    # Filter by category slug
    if category:
        query = query.join(Category).where(Category.slug == category.lower())

    # Search by name or model number
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Product.name.ilike(search_pattern),
                Product.model_number.ilike(search_pattern),
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(Product.name).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    products = result.scalars().all()

    # Convert to public response (exclude internal fields)
    items = []
    for p in products:
        items.append(
            PublicProductResponse(
                id=p.id,
                name=p.name,
                slug=p.slug,
                summary=p.summary,
                description=p.description,
                catalogue_price={"amount": str(p.catalogue_price_amount)} if p.catalogue_price_amount else None,
                currency_code=p.currency_code,
                brand=BrandResponse.model_validate(p.brand) if p.brand else None,
                category=CategoryResponse.model_validate(p.category) if p.category else None,
            )
        )

    return PublicProductListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/products/{slug_or_id}", response_model=PublicProductResponse)
async def get_public_product(
    slug_or_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a published product by slug or ID."""
    # Try to parse as UUID first
    try:
        product_id = UUID(slug_or_id)
        query = (
            select(Product)
            .options(selectinload(Product.brand), selectinload(Product.category))
            .where(Product.id == product_id, Product.status == "published")
        )
    except ValueError:
        # Not a UUID, treat as slug
        query = (
            select(Product)
            .options(selectinload(Product.brand), selectinload(Product.category))
            .where(Product.slug == slug_or_id.lower(), Product.status == "published")
        )

    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{slug_or_id}' not found",
        )

    return PublicProductResponse(
        id=product.id,
        name=product.name,
        slug=product.slug,
        summary=product.summary,
        description=product.description,
        catalogue_price={"amount": str(product.catalogue_price_amount)} if product.catalogue_price_amount else None,
        currency_code=product.currency_code,
        brand=BrandResponse.model_validate(product.brand) if product.brand else None,
        category=CategoryResponse.model_validate(product.category) if product.category else None,
    )


@router.get("/brands", response_model=list[BrandResponse])
async def list_public_brands(
    db: AsyncSession = Depends(get_db_session),
):
    """List all active brands."""
    result = await db.execute(
        select(Brand)
        .where(Brand.status == "active")
        .order_by(Brand.name)
    )
    brands = result.scalars().all()
    return brands


@router.get("/brands/{slug}", response_model=BrandResponse)
async def get_public_brand(
    slug: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get an active brand by slug."""
    result = await db.execute(
        select(Brand).where(Brand.slug == slug.lower(), Brand.status == "active")
    )
    brand = result.scalar_one_or_none()

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand '{slug}' not found",
        )

    return brand


@router.get("/categories", response_model=list[CategoryResponse])
async def list_public_categories(
    db: AsyncSession = Depends(get_db_session),
):
    """List all active categories."""
    result = await db.execute(
        select(Category)
        .options(selectinload(Category.parent))
        .where(Category.status == "active")
        .order_by(Category.sort_order, Category.name)
    )
    categories = result.scalars().all()
    return categories


@router.get("/categories/{slug}", response_model=CategoryResponse)
async def get_public_category(
    slug: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get an active category by slug."""
    result = await db.execute(
        select(Category)
        .options(selectinload(Category.parent))
        .where(Category.slug == slug.lower(), Category.status == "active")
    )
    category = result.scalar_one_or_none()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{slug}' not found",
        )

    return category
