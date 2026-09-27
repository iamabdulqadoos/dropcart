from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReservationCreate(BaseModel):
    user_id: int


class ReservationResponse(BaseModel):
    id: int
    drop_id: int
    user_id: int
    status: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)