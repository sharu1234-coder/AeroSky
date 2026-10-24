from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Passenger(Base):
    __tablename__ = "passengers"

    __table_args__ = (
        CheckConstraint(
            "passenger_type IN ('adult', 'child')",
            name="ck_passengers_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    passenger_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    flight_seat_id: Mapped[int | None] = mapped_column(
        ForeignKey("flight_seats.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )

    flight_seat = relationship(
        "FlightSeat",
        back_populates="passenger",
    )

    booking = relationship(
        "Booking",
        back_populates="passengers",
    )
