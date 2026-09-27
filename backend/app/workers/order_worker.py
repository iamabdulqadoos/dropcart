import asyncio

from celery import shared_task
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.order import Order


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_order(self, order_id: int):

    try:
        return asyncio.run(
            _process_order(order_id)
        )

    except Exception:
        asyncio.run(
            _mark_order_failed(order_id)
        )

        raise


async def _process_order(order_id: int):

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Order).where(
                Order.id == order_id
            )
        )

        order = result.scalar_one_or_none()

        if not order:
            return {
                "status": "failed",
                "message": "Order not found",
            }

        order.status = "processing"

        await db.commit()

        await asyncio.sleep(5)

        order.status = "completed"

        await db.commit()

        return {
            "status": "completed",
            "order_id": order_id,
        }


async def _mark_order_failed(order_id: int):

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Order).where(
                Order.id == order_id
            )
        )

        order = result.scalar_one_or_none()

        if order:
            order.status = "failed"
            await db.commit()