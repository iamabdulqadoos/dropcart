from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.payment import CheckoutResponse
from app.services.payment_service import create_checkout


router = APIRouter(
    prefix="/reservations",
    tags=["Checkout"],
)


@router.post(
    "/{reservation_id}/checkout",
    response_model=CheckoutResponse,
)
async def checkout(
    reservation_id: int,
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
    ),
    db: AsyncSession = Depends(get_db),
):

    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail="IDEMPOTENCY_KEY_REQUIRED",
        )

    payment_intent = await create_checkout(
        db=db,
        reservation_id=reservation_id,
        idempotency_key=idempotency_key,
    )

    return CheckoutResponse(
        reservation_id=payment_intent.reservation_id,
        payment_intent_id=payment_intent.id,
        payment_id=payment_intent.payment_id,
        amount=float(payment_intent.amount),
        currency=payment_intent.currency,
        status=payment_intent.status,
    )