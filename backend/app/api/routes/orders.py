from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from app.schemas.order import OrderResponse

from app.services.order_service import (
    checkout_cart,
    get_order,
    get_user_orders,
)
from app.workers.order_worker import (
    process_order,
)


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
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):

    try:

        order = await checkout_cart(
            db,
            user_id,
        )

        background_tasks.add_task(
            process_order,
            order["id"],
        )

        return order

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

@router.get(
    "/user/{user_id}",
    response_model=list[OrderResponse],
)
async def get_user_order_history(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_user_orders(
        db,
        user_id,
    )

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
async def get_order_details(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):

    try:

        return await get_order(
            db,
            order_id,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )