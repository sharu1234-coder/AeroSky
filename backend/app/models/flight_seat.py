from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FlightSeat(Base):
    __tablename__ = "flight_seats"

    __table_args__ = (
        UniqueConstraint(
            "flight_id",
            "seat_number",
            name="uq_flight_seats_flight_number",
        ),
        CheckConstraint(
            "seat_row >= 1",
            name="ck_flight_seats_row_positive",
        ),
        CheckConstraint(
            "status IN ('available', 'held', 'booked')",
            name="ck_flight_seats_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    flight_id: Mapped[int] = mapped_column(
        ForeignKey("flights.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    seat_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    seat_row: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    seat_column: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    cabin_class: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="available",
        nullable=False,
    )

    flight = relationship("Flight", back_populates="seats")

    passenger = relationship(
        "Passenger",
        back_populates="flight_seat",
        uselist=False,
    )
