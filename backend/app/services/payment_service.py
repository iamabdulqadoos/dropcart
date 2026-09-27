from datetime import datetime, timezone

import os
import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.drop import Drop
from app.models.payment_intent import PaymentIntent
from app.models.product import Product
from app.models.reservation import Reservation
from app.services.state_machine import transition_reservation


PAYMENT_GATEWAY_URL = os.getenv(
    "PAYMENT_GATEWAY_URL",
    "http://127.0.0.1:9000",
)


async def create_checkout(
    db: AsyncSession,
    reservation_id: int,
    idempotency_key: str,
):
    # 1. Find reservation
    result = await db.execute(
        select(Reservation)
        .where(Reservation.id == reservation_id)
        .with_for_update()
    )

    reservation = result.scalar_one_or_none()

    if not reservation:
        raise HTTPException(
            status_code=404,
            detail="RESERVATION_NOT_FOUND",
        )

    # 2. Check idempotency key
    existing_result = await db.execute(
        select(PaymentIntent)
        .where(
            PaymentIntent.idempotency_key == idempotency_key
        )
    )

    existing_payment = existing_result.scalar_one_or_none()

    if existing_payment:
        return existing_payment

    # 3. Reservation must be active
    if reservation.status != "active":
        raise HTTPException(
            status_code=409,
            detail="RESERVATION_NOT_ACTIVE",
        )

    # 4. Check expiration
    now = datetime.now(timezone.utc)

    if reservation.expires_at <= now:

        await transition_reservation(
            db=db,
            reservation=reservation,
            new_status="expired",
            source="user",
        )

        await db.commit()

        raise HTTPException(
            status_code=409,
            detail="RESERVATION_EXPIRED",
        )

    # 5. Get Drop
    drop_result = await db.execute(
        select(Drop)
        .where(Drop.id == reservation.drop_id)
    )

    drop = drop_result.scalar_one_or_none()

    if not drop:
        raise HTTPException(
            status_code=404,
            detail="DROP_NOT_FOUND",
        )

    # 6. Get Product
    product_result = await db.execute(
        select(Product)
        .where(Product.id == drop.product_id)
    )

    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="PRODUCT_NOT_FOUND",
        )

    # 7. Create PaymentIntent
    payment_intent = PaymentIntent(
        reservation_id=reservation.id,
        idempotency_key=idempotency_key,
        amount=product.price,
        currency="PKR",
        status="payment_pending",
        created_at=now,
        updated_at=now,
    )

    db.add(payment_intent)

    await db.flush()

    # 8. Move reservation:
    # active -> payment_pending
    await transition_reservation(
        db=db,
        reservation=reservation,
        new_status="payment_pending",
        source="user",
    )

    await db.commit()

    await db.refresh(payment_intent)

    # 9. Call Mock Payment Gateway
    try:

        async with httpx.AsyncClient(timeout=10) as client:

            response = await client.post(
                f"{PAYMENT_GATEWAY_URL}/payments",
                json={
                    "payment_intent_id": str(
                        payment_intent.id
                    ),
                    "amount": float(product.price),
                    "currency": "PKR",
                },
            )

    except httpx.RequestError:

        await db.refresh(payment_intent)
        await db.refresh(reservation)

        await transition_reservation(
            db=db,
            reservation=reservation,
            new_status="failed",
            source="user",
        )

        payment_intent.status = "failed"
        payment_intent.updated_at = (
            datetime.now(timezone.utc)
        )

        await db.commit()

        raise HTTPException(
            status_code=502,
            detail="PAYMENT_GATEWAY_UNAVAILABLE",
        )

    # 10. Gateway rejected request
    if response.status_code >= 400:

        await db.refresh(payment_intent)
        await db.refresh(reservation)

        await transition_reservation(
            db=db,
            reservation=reservation,
            new_status="failed",
            source="user",
        )

        payment_intent.status = "failed"
        payment_intent.updated_at = (
            datetime.now(timezone.utc)
        )

        await db.commit()

        raise HTTPException(
            status_code=502,
            detail="PAYMENT_GATEWAY_ERROR",
        )

    # 11. Save gateway payment ID
    gateway_data = response.json()

    payment_intent.payment_id = gateway_data["payment_id"]

    payment_intent.updated_at = (
        datetime.now(timezone.utc)
    )

    await db.commit()

    await db.refresh(payment_intent)

    return payment_intent