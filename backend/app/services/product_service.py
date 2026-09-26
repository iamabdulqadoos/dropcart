from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate


async def create_product(
    db: AsyncSession,
    product_data: ProductCreate,
):
    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
    )

    db.add(product)

    await db.commit()
    await db.refresh(product)

    return product


async def get_products(
    db: AsyncSession,
):
    result = await db.execute(
        select(Product)
    )

    return result.scalars().all()