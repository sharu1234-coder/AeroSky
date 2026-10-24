from sqlalchemy import ForeignKey
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )


    __table_args__ = (
        CheckConstraint(
            "passenger_count >= 1 AND passenger_count <= 9",
            name="ck_bookings_passenger_count",
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="ck_bookings_total_amount",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    booking_reference: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True,
        nullable=False,
    )

    flight_id: Mapped[int] = mapped_column(
        ForeignKey("flights.id"),
        nullable=False,
        index=True,
    )

    passenger_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )

    contact_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    contact_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
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

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    payments = relationship(
        "Payment",
        back_populates="booking",
    )

    flight = relationship("Flight")

    passengers = relationship(
        "Passenger",
        back_populates="booking",
        cascade="all, delete-orphan",
    )
