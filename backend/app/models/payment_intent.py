from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PaymentIntent(Base):
    __tablename__ = "payment_intents"

    id: Mapped[int] = mapped_column(primary_key=True)

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id"),
        nullable=False,
    )

    payment_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="PKR",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="payment_pending",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    reservation = relationship("Reservation")

    __table_args__ = (
        UniqueConstraint(
            "idempotency_key",
            name="uq_payment_intent_idempotency_key",
        ),
    )