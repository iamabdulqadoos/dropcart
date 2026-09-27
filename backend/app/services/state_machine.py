from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reservation import Reservation
from app.models.state_transition import StateTransition


ALLOWED_TRANSITIONS = {
    "active": {
        "payment_pending",
        "expired",
    },
    "payment_pending": {
        "paid",
        "failed",
        "expired",
    },
    "paid": {
        "confirmed",
        "refunded",
    },
    "confirmed": {
        "refunded",
    },
    "failed": set(),
    "expired": set(),
    "refunded": set(),
}


async def transition_reservation(
    db: AsyncSession,
    reservation: Reservation,
    new_status: str,
    source: str,
) -> Reservation:

    current_status = reservation.status

    allowed_statuses = ALLOWED_TRANSITIONS.get(
        current_status,
        set(),
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=409,
            detail=(
                f"INVALID_STATE_TRANSITION: "
                f"{current_status} -> {new_status}"
            ),
        )

    transition = StateTransition(
        reservation_id=reservation.id,
        from_status=current_status,
        to_status=new_status,
        source=source,
        created_at=datetime.now(timezone.utc),
    )

    reservation.status = new_status

    db.add(transition)

    await db.flush()

    return reservation