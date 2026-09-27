import hashlib
import hmac
import json
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.payment_event import PaymentEvent
from app.models.payment_intent import PaymentIntent
from app.models.reservation import Reservation
from app.services.state_machine import transition_reservation


router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)

WEBHOOK_SECRET = "dropcart-webhook-secret"

MAX_WEBHOOK_AGE = 5 * 60


def verify_signature(
    payload: bytes,
    signature: str,
) -> bool:

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature,
    )


@router.post("/payment")
async def payment_webhook(
    request: Request,
    x_webhook_signature: str | None = Header(
        default=None,
        alias="X-Webhook-Signature",
    ),
    x_webhook_timestamp: str | None = Header(
        default=None,
        alias="X-Webhook-Timestamp",
    ),
):

    # ---------------------------------------------
    # 1. Read raw body
    # ---------------------------------------------

    payload = await request.body()

    if not x_webhook_signature:

        raise HTTPException(
            status_code=401,
            detail="MISSING_WEBHOOK_SIGNATURE",
        )

    if not x_webhook_timestamp:

        raise HTTPException(
            status_code=401,
            detail="MISSING_WEBHOOK_TIMESTAMP",
        )

    # ---------------------------------------------
    # 2. Replay protection
    # ---------------------------------------------

    try:

        timestamp = int(x_webhook_timestamp)

    except ValueError:

        raise HTTPException(
            status_code=401,
            detail="INVALID_WEBHOOK_TIMESTAMP",
        )

    now = int(time.time())

    if abs(now - timestamp) > MAX_WEBHOOK_AGE:

        raise HTTPException(
            status_code=401,
            detail="WEBHOOK_EXPIRED",
        )

    # ---------------------------------------------
    # 3. Verify HMAC
    # ---------------------------------------------

    if not verify_signature(
        payload,
        x_webhook_signature,
    ):

        raise HTTPException(
            status_code=401,
            detail="INVALID_WEBHOOK_SIGNATURE",
        )

    # ---------------------------------------------
    # 4. Parse JSON
    # ---------------------------------------------

    try:

        data = json.loads(payload)

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=400,
            detail="INVALID_JSON",
        )

    event_id = data.get("event_id")
    event_type = data.get("event_type")
    payment_intent_id = data.get(
        "payment_intent_id"
    )

    if not event_id or not event_type or not payment_intent_id:

        raise HTTPException(
            status_code=400,
            detail="INVALID_WEBHOOK_EVENT",
        )

    # ---------------------------------------------
    # 5. Database transaction
    # ---------------------------------------------

    async with AsyncSessionLocal() as db:

        # -----------------------------------------
        # Duplicate webhook protection
        # -----------------------------------------

        existing_event_result = await db.execute(
            select(PaymentEvent)
            .where(
                PaymentEvent.event_id == event_id
            )
        )

        existing_event = (
            existing_event_result.scalar_one_or_none()
        )

        if existing_event:

            return {
                "status": "duplicate",
                "event_id": event_id,
            }

        # -----------------------------------------
        # Find PaymentIntent
        # -----------------------------------------

        payment_result = await db.execute(
            select(PaymentIntent)
            .where(
                PaymentIntent.id
                == int(payment_intent_id)
            )
            .with_for_update()
        )

        payment_intent = (
            payment_result.scalar_one_or_none()
        )

        if not payment_intent:

            raise HTTPException(
                status_code=404,
                detail="PAYMENT_INTENT_NOT_FOUND",
            )

        # -----------------------------------------
        # Find Reservation
        # -----------------------------------------

        reservation_result = await db.execute(
            select(Reservation)
            .where(
                Reservation.id
                == payment_intent.reservation_id
            )
            .with_for_update()
        )

        reservation = (
            reservation_result.scalar_one_or_none()
        )

        if not reservation:

            raise HTTPException(
                status_code=404,
                detail="RESERVATION_NOT_FOUND",
            )

        # -----------------------------------------
        # Create event record
        # -----------------------------------------

        event = PaymentEvent(
            event_id=event_id,
            event_type=event_type,
            payment_intent_id=payment_intent_id,
            payload=payload.decode(),
            received_at=datetime.now(timezone.utc),
        )

        db.add(event)

        # -----------------------------------------
        # SUCCESS
        # -----------------------------------------

        if event_type == "payment.succeeded":

            if payment_intent.status != "payment_pending":

                raise HTTPException(
                    status_code=409,
                    detail="INVALID_PAYMENT_STATE",
                )

            # PaymentIntent:
            # payment_pending -> paid
            payment_intent.status = "paid"

            payment_intent.updated_at = (
                datetime.now(timezone.utc)
            )

            # Reservation:
            # payment_pending -> paid
            await transition_reservation(
                db=db,
                reservation=reservation,
                new_status="paid",
                source="webhook",
            )

        # -----------------------------------------
        # FAILURE
        # -----------------------------------------

        elif event_type == "payment.failed":

            if payment_intent.status != "payment_pending":

                raise HTTPException(
                    status_code=409,
                    detail="INVALID_PAYMENT_STATE",
                )

            # PaymentIntent:
            # payment_pending -> failed
            payment_intent.status = "failed"

            payment_intent.updated_at = (
                datetime.now(timezone.utc)
            )

            # Reservation:
            # payment_pending -> failed
            await transition_reservation(
                db=db,
                reservation=reservation,
                new_status="failed",
                source="webhook",
            )

        else:

            raise HTTPException(
                status_code=400,
                detail="UNKNOWN_EVENT_TYPE",
            )

        await db.commit()

    return {
        "status": "processed",
        "event_id": event_id,
    }