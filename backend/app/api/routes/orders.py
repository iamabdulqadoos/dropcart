from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.order import OrderResponse
from app.services.order_service import checkout_cart


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "/checkout/{user_id}",
    response_model=OrderResponse,
)
async def checkout(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:

        return await checkout_cart(
            db,
            user_id,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )