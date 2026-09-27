from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StateTransition(Base):
    __tablename__ = "state_transitions"

    id: Mapped[int] = mapped_column(primary_key=True)

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id"),
        nullable=False,
    )

    from_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    to_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )