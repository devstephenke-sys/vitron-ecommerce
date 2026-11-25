"""Admin catalogue router."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db_session
from app.modules.catalogue.deps import (
    get_brand,
    get_category,
    get_product,
    require_catalog_publish,
    require_catalog_read,
    require_catalog_write,
)
from app.modules.catalogue.models import Brand, Category, Product
from app.modules.catalogue.schemas import (
    BrandCreate,
    BrandResponse,
    BrandUpdate,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ProductCreate,
    ProductListResponse,
    ProductPublishRequest,
    ProductPublishResponse,
    ProductResponse,
    ProductUpdate,
)
from app.modules.platform.audit import record_audit

router = APIRouter(prefix="/admin/catalog", tags=["admin-catalog"])


# Brand endpoints
@router.get("/brands", response_model=list[BrandResponse])
async def list_brands(
    db: AsyncSession = Depends(get_db_session),
    _auth=Depends(require_catalog_read),
):
    """List all brands."""
    from sqlalchemy import select

    result = await db.execute(select(Brand).order_by(Brand.name))
    brands = result.scalars().all()
    return brands


@router.post("/brands", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand_in: BrandCreate,
    db: AsyncSession = Depends(get_db_session),
    auth_user=Depends(require_catalog_write),
):
    """Create a new brand."""
    from sqlalchemy import select

    # Check slug uniqueness
    existing = await db.execute(
        select(Brand).where(Brand.slug == brand_in.slug.lower())
    )
    if existing.scalar_one_or_none():
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Brand with slug '{brand_in.slug}' already exists",
        )

    brand = Brand(**brand_in.model_dump())
    db.add(brand)
    await db.commit()
    await db.refresh(brand)

    await record_audit(
        db,
        actor_user_id=auth_user.id,
        action="brand.create",
        entity_type="brand",
        entity_id=str(brand.id),
        after=brand_in.model_dump(),
    )

    return brand


@router.get("/brands/{brand_id}", response_model=BrandResponse)
async def get_brand_by_id(
    brand: Brand = Depends(get_brand),
    _auth=Depends(require_catalog_read),
):
    """Get a brand by ID."""
    return brand


@router.patch("/brands/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_in: BrandUpdate,
    brand: Brand = Depends(get_brand),
    db: AsyncSession = Depends(get_db_session),
    auth_user=Depends(require_catalog_write),
):
    """Update a brand."""
    from sqlalchemy import select

    before = brand.model_dump()

    # Check slug uniqueness if changing
    if brand_in.slug and brand_in.slug != brand.slug:
        existing = await db.execute(
            select(Brand).where(Brand.slug == brand_in.slug.lower())
        )
        if existing.scalar_one_or_none():
            from fastapi import HTTPException

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Brand with slug '{brand_in.slug}' already exists",
            )

    update_data = brand_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand, field, value)

    await db.commit()
    await db.refresh(brand)

    await record_audit(
        db,
        actor_user_id=auth_user.id,
        action="brand.update",
        entity_type="brand",
        entity_id=str(brand.id),
        before=before,
        after=brand.model_dump(),
    )

    return brand


@router.delete("/brands/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(
    brand: Brand = Depends(get_brand),
    db: AsyncSession = Depends(get_db_session),
    auth_user=Depends(require_catalog_write),
):
    """Archive a brand (soft delete via status)."""
    before = brand.model_dump()

    brand.status = "archived"
    await db.commit()

    await record_audit(
        db,
        actor_user_id=auth_user.id,
        action="brand.delete",
        entity_type="brand",
        entity_id=str(brand.id),
        before=before,
        after={"status": "archived"},
    )


# Category endpoints
@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db_session),
    _auth=Depends(require_catalog_read),
):
    """List all categories."""
    from sqlalchemy import select

    result = await db.execute(
        select(Category)
        .options(selectinload(Category.parent))
        .order_by(Category.sort_order, Category.name)
    )
    categories = result.scalars().all()
    return categories


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db_session),
    auth_user=Depends(require_catalog_write),
):
    """Create a new category."""
    from sqlalchemy import select

    # Check slug uniqueness
    existing = await db.execute(
        select(Category).where(Category.slug == category_in.slug.lower())
    )
    if existing.scalar_one_or_none():
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with slug '{category_in.slug}' already exists",
        )

    # Validate parent exists if provided
    if category_in.parent_id:
        parent = await db.execute(
            select(Category).where(Category.id == category_in.parent_id)
        )
        if not parent.scalar_one_or_none():
            from fastapi import HTTPException

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent category {category_in.parent_id} not found",
            )

    category = Category(**category_in.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)

    await record_audit(
        db,
        actor_user_id=auth_user.id,
        action="category.create",
        entity_type="category",
        entity_id=str(category.id),
        after=category_in.model_dump(),
    )

    return category


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(
    category: Category = Depends(get_category),
    _auth=Depends(require_catalog_read),
):
    """Get a category by ID."""
    return category


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_in: CategoryUpdate,
    category: Category = Depends(get_category),
    db: AsyncSession = Depends(get_db_session),
    auth_user=Depends(require_catalog_write),
):
    """Update a category."""
    from sqlalchemy import select

    before = category.model_dump()

    # Check slug uniqueness if changing
    if category_in.slug and category_in.slug != category.slug:
        existing = await db.execute(
            select(Category).where(Category.slug == category_in.slug.lower())
        )
        if existing.scalar_one_or_none():
            from fastapi import HTTPException

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category with slug '{category_in.slug}' already exists",
            )

    # Validate parent exists if changing
    if category_in.parent_id is not None:
        parent = await db.execute(
            select(Category).where(Category.id == category_in.parent_id)
        )
        if not parent.scalar_one_or_none():
            from fastapi import HTTPException

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent category {category_in.parent_id} not found",
            )

    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    await record_audit(
        db,
        actor_user_id=auth_user.id,
        action="category.update",
        entity_type="category",
        entity_id=str(category.id),
        before=before,
        after=category.model_dump(),
    )

    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category: Category = Depends(get_category),
    db: AsyncSession = Depends(get_db_session),
    auth_user=Depends(require_catalog_write),
):
    """Archive a category (soft delete via status)."""
    before = category.model_dump()

    category.status = "archived"
    await db.commit()

    await record_audit(
        db,
        actor_user_id=auth_user.id,
        action="category.delete",
        entity_type="category",
        entity_id=str(category.id),
        before=before,
        after={"status": "archived"},
    )


# Product endpoints
@router.get("/products", response_model=ProductListResponse)
async def list_products(
    page: int = 1,
    page_size: int = 50,
    status: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    _auth=Depends(require_catalog_read),
):
    """List products with pagination and optional status filter."""
    from sqlalchemy import select, func

    query = select(Product).options(
        selectinload(Product.brand),
        selectinload(Product.category),
    )

    if status:
        query = query.where(Product.status == status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    products = result.scalars().all()

    return ProductListResponse(
        items=products,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db_session),
    auth_user=Depends(require_catalog_write),
):
    """Create a new product."""
    from sqlalchemy import select

    # Check slug uniqueness
    existing = await db.execute(
        select(Product).where(Product.slug == product_in.slug.lower())
    )
    if existing.scalar_one_or_none():
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with slug '{product_in.slug}' already exists",
        )

    # Validate brand exists if provided
    if product_in.brand_id:
        brand = await db.execute(
            select(Brand).where(Brand.id == product_in.brand_id)
        )
        if not brand.scalar_one_or_none():
            from fastapi import HTTPException

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand {product_in.brand_id} not found",
            )

    # Validate category exists if provided
    if product_in.category_id:
        category = await db.execute(
            select(Category).where(Category.id == product_in.category_id)
        )
        if not category.scalar_one_or_none():
            from fastapi import HTTPException

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {product_in.category_id} not found",
            )

    # Parse money fields
    product_data = product_in.model_dump()
    if product_in.catalogue_price:
        product_data["catalogue_price_amount"] = product_in.catalogue_price.amount
        product_data["currency_code"] = product_in.catalogue_price.currency
        del product_data["catalogue_price"]

    product = Product(**product_data)
    db.add(product)
    await db.commit()
    await db.refresh(product)

    await record_audit(
        db,
        actor_user_id=auth_user.id,
        action="product.create",
        entity_type="product",
        entity_id=str(product.id),
        after=product_in.model_dump(),
    )

    return product


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product: Product = Depends(get_product),
    _auth=Depends(require_catalog_read),
):
    """Get a product by ID."""
    return product


@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_in: ProductUpdate,
    product: Product = Depends(get_product),
    db: AsyncSession = Depends(get_db_session),
    auth_user=Depends(require_catalog_write),
):
    """Update a product."""
    from sqlalchemy import select

    before = product.model_dump()

    # Check slug uniqueness if changing
    if product_in.slug and product_in.slug != product.slug:
        existing = await db.execute(
            select(Product).where(Product.slug == product_in.slug.lower())
        )
        if existing.scalar_one_or_none():
            from fastapi import HTTPException

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with slug '{product_in.slug}' already exists",
            )

    # Validate brand exists if changing
    if product_in.brand_id is not None:
        brand = await db.execute(
            select(Brand).where(Brand.id == product_in.brand_id)
        )
        if not brand.scalar_one_or_none():
            from fastapi import HTTPException

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand {product_in.brand_id} not found",
            )

    # Validate category exists if changing
    if product_in.category_id is not None:
        category = await db.execute(
            select(Category).where(Category.id == product_in.category_id)
        )
        if not category.scalar_one_or_none():
            from fastapi import HTTPException

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {product_in.category_id} not found",
            )

    update_data = product_in.model_dump(exclude_unset=True)

    # Handle money field
    if "catalogue_price" in update_data:
        if update_data["catalogue_price"] is not None:
            update_data["catalogue_price_amount"] = update_data["catalogue_price"].amount
            update_data["currency_code"] = update_data["catalogue_price"].currency
        else:
            update_data["catalogue_price_amount"] = None
            update_data["currency_code"] = None
        del update_data["catalogue_price"]

    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    await record_audit(
        db,
        actor_user_id=auth_user.id,
        action="product.update",
        entity_type="product",
        entity_id=str(product.id),
        before=before,
        after=product.model_dump(),
    )

    return product


@router.post("/products/{product_id}/publish", response_model=ProductPublishResponse)
async def publish_product(
    _request: ProductPublishRequest,
    product: Product = Depends(get_product),
    db: AsyncSession = Depends(get_db_session),
    auth_user=Depends(require_catalog_publish),
):
    """Publish a product after validation."""
    from datetime import datetime, timezone
    from sqlalchemy import select
    from app.modules.catalogue.models import ProductImage

    validation_errors = []

    # Validation: must have a brand
    if not product.brand_id:
        validation_errors.append("Product must have a brand assigned")

    # Validation: must have a category
    if not product.category_id:
        validation_errors.append("Product must have a category assigned")

    # Validation: must have a price
    if not product.catalogue_price_amount:
        validation_errors.append("Product must have a catalogue price")

    # Validation: must have at least one verified image (BD-10)
    image_result = await db.execute(
        select(ProductImage).where(
            ProductImage.product_id == product.id,
            ProductImage.status == "verified"
        )
    )
    if not image_result.scalar_one_or_none():
        validation_errors.append("Product must have at least one verified image")

    if validation_errors:
        return ProductPublishResponse(
            product_id=product.id,
            status=product.status,
            validation_errors=validation_errors,
        )

    # All validations passed
    before = product.model_dump()
    product.status = "published"
    product.published_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(product)

    await record_audit(
        db,
        actor_user_id=auth_user.id,
        action="product.publish",
        entity_type="product",
        entity_id=str(product.id),
        before=before,
        after=product.model_dump(),
    )

    return ProductPublishResponse(
        product_id=product.id,
        status=product.status,
        published_at=product.published_at,
    )
