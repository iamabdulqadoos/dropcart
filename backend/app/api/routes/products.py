from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import (
    create_product,
    get_products,
)


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "/",
    response_model=ProductResponse,
)
async def create_new_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_product(
        db,
        product_data,
    )


@router.get(
    "/",
    response_model=list[ProductResponse],
)
async def list_products(
    db: AsyncSession = Depends(get_db),
):
    return await get_products(db)