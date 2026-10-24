from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint(
            "amount_paise > 0",
            name="ck_payments_positive_amount",
        ),
        CheckConstraint(
            "status IN ('created', 'authorized', 'captured', 'failed', 'refunded')",
            name="ck_payments_valid_status",
        ),
        UniqueConstraint(
            "razorpay_order_id",
            name="uq_payments_razorpay_order_id",
        ),
        UniqueConstraint(
            "razorpay_payment_id",
            name="uq_payments_razorpay_payment_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id"),
        nullable=False,
        index=True,
    )

    razorpay_order_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    razorpay_payment_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    amount_paise: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="created",
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    booking = relationship(
        "Booking",
        back_populates="payments",
    )
