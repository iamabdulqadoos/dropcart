from pydantic import BaseModel


class CheckoutResponse(BaseModel):
    reservation_id: int
    payment_intent_id: int
    payment_id: str | None
    amount: float
    currency: str
    status: str