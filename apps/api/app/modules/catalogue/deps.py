"""Dependencies for catalogue endpoints."""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.catalogue.models import Brand, Category, Product
from app.modules.identity.deps import require_permission


async def get_brand(
    brand_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> Brand:
    """Get a brand by ID or raise 404."""
    from sqlalchemy import select

    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand {brand_id} not found",
        )
    return brand


async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> Category:
    """Get a category by ID or raise 404."""
    from sqlalchemy import select

    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found",
        )
    return category


async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> Product:
    """Get a product by ID or raise 404."""
    from sqlalchemy import select

    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found",
        )
    return product


# Permission dependencies for catalogue operations
require_catalog_read = require_permission("catalog.read")
require_catalog_write = require_permission("catalog.write")
require_catalog_publish = require_permission("catalog.publish")
