from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
)
from app.services.reservation_service import create_reservation


router = APIRouter(
    prefix="/drops",
    tags=["Drops"],
)


@router.post(
    "/{drop_id}/reserve",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def reserve_drop(
    drop_id: int,
    data: ReservationCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_reservation(
        db=db,
        drop_id=drop_id,
        user_id=data.user_id,
    )