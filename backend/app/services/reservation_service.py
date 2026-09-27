from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.drop import Drop
from app.models.reservation import Reservation


RESERVATION_MINUTES = 5


async def create_reservation(
    db: AsyncSession,
    drop_id: int,
    user_id: int,
):
    async with db.begin():

        # Lock the drop row so concurrent requests
        # cannot reserve the same inventory simultaneously.
        result = await db.execute(
            select(Drop)
            .where(Drop.id == drop_id)
            .with_for_update()
        )

        drop = result.scalar_one_or_none()

        if not drop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drop not found",
            )

        now = datetime.now(timezone.utc)

        # Check whether the drop is currently live.
        if now < drop.starts_at:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="DROP_NOT_STARTED",
            )

        if now > drop.ends_at:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="DROP_ENDED",
            )

        # Check for an existing active reservation
        # belonging to this user.
        existing_result = await db.execute(
            select(Reservation)
            .where(
                Reservation.drop_id == drop_id,
                Reservation.user_id == user_id,
                Reservation.status == "active",
                Reservation.expires_at > now,
            )
        )

        existing = existing_result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="USER_ALREADY_RESERVED",
            )

        # Count currently active reservations.
        count_result = await db.execute(
            select(func.count(Reservation.id))
            .where(
                Reservation.drop_id == drop_id,
                Reservation.status == "active",
                Reservation.expires_at > now,
            )
        )

        active_reservations = count_result.scalar_one()

        if active_reservations >= drop.quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SOLD_OUT",
            )

        expires_at = now + timedelta(
            minutes=RESERVATION_MINUTES
        )

        reservation = Reservation(
            drop_id=drop_id,
            user_id=user_id,
            status="active",
            expires_at=expires_at,
            created_at=now,
        )

        db.add(reservation)

        await db.flush()

        return reservation