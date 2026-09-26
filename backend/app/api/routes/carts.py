from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse,
    CartResponse,
)
from app.services.cart_service import (
    add_to_cart,
    get_cart,
    update_cart_item,
    remove_cart_item,
)


router = APIRouter(
    prefix="/carts",
    tags=["Carts"],
)


@router.post(
    "/{user_id}/items",
    response_model=CartItemResponse,
)
async def add_product_to_cart(
    user_id: int,
    item_data: CartItemCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await add_to_cart(
            db,
            user_id,
            item_data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get(
    "/{user_id}",
    response_model=CartResponse,
)
async def get_user_cart(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        cart, items = await get_cart(
            db,
            user_id,
        )

        return {
            "id": cart.id,
            "user_id": cart.user_id,
            "items": items,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.patch(
    "/{user_id}/items/{item_id}",
    response_model=CartItemResponse,
)
async def update_cart_item_quantity(
    user_id: int,
    item_id: int,
    item_data: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await update_cart_item(
            db,
            user_id,
            item_id,
            item_data.quantity,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.delete(
    "/{user_id}/items/{item_id}",
)
async def delete_cart_item(
    user_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await remove_cart_item(
            db,
            user_id,
            item_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )