import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.reservation import Reservation
from app.workers.celery_app import celery_app


async def _expire_reservations():
    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Reservation).where(
                Reservation.status == "active",
                Reservation.expires_at <= now,
            )
        )

        reservations = result.scalars().all()

        expired_count = 0

        for reservation in reservations:
            reservation.status = "expired"
            expired_count += 1

        await db.commit()

        return expired_count


@celery_app.task
def expire_reservations():
    return asyncio.run(_expire_reservations())