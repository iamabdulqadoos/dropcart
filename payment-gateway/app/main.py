import asyncio
import hashlib
import hmac
import os
import random
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="DropCart Mock Payment Gateway")


WEBHOOK_SECRET = os.getenv(
    "WEBHOOK_SECRET",
    "dropcart-webhook-secret",
)

API_WEBHOOK_URL = os.getenv(
    "API_WEBHOOK_URL",
    "http://api:8000/webhooks/payment",
)


class PaymentRequest(BaseModel):
    payment_intent_id: str
    amount: float
    currency: str = "PKR"


def generate_signature(payload: str) -> str:
    return hmac.new(
        WEBHOOK_SECRET.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/payments")
async def create_payment(data: PaymentRequest):

    payment_id = str(uuid.uuid4())

    asyncio.create_task(
        process_payment(
            payment_id=payment_id,
            payment_intent_id=data.payment_intent_id,
            amount=data.amount,
        )
    )

    return {
        "payment_id": payment_id,
        "payment_intent_id": data.payment_intent_id,
        "status": "pending",
    }


async def process_payment(
    payment_id: str,
    payment_intent_id: str,
    amount: float,
):
    # Random delay between 0 and 30 seconds.
    delay = random.uniform(0, 30)

    await asyncio.sleep(delay)

    # Approximately 10% payment failures.
    succeeded = random.random() >= 0.10

    event_type = (
        "payment.succeeded"
        if succeeded
        else "payment.failed"
    )

    event_id = str(uuid.uuid4())

    timestamp = int(
        datetime.now(timezone.utc).timestamp()
    )

    payload = (
        f'{{'
        f'"event_id":"{event_id}",'
        f'"event_type":"{event_type}",'
        f'"payment_id":"{payment_id}",'
        f'"payment_intent_id":"{payment_intent_id}",'
        f'"amount":{amount},'
        f'"timestamp":{timestamp}'
        f'}}'
    )

    signature = generate_signature(payload)

    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
        "X-Webhook-Timestamp": str(timestamp),
    }

    async with httpx.AsyncClient() as client:

        # First webhook
        await client.post(
            API_WEBHOOK_URL,
            content=payload,
            headers=headers,
        )

        # Occasionally send duplicate webhooks.
        if random.random() < 0.7:
            await asyncio.sleep(0.5)

            await client.post(
                API_WEBHOOK_URL,
                content=payload,
                headers=headers,
            )