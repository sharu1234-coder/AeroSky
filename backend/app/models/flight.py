from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[int] = mapped_column(primary_key=True)

    flight_number: Mapped[str] = mapped_column(
        String(15), index=True
    )

    airline_id: Mapped[int] = mapped_column(
        ForeignKey("airlines.id")
    )

    aircraft_id: Mapped[int | None] = mapped_column(
        ForeignKey("aircraft.id"),
        nullable=True,
        index=True,
    )

    origin_id: Mapped[int] = mapped_column(
        ForeignKey("airports.id")
    )

    destination_id: Mapped[int] = mapped_column(
        ForeignKey("airports.id")
    )

    departure_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    arrival_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2)
    )

    available_seats: Mapped[int] = mapped_column(
        Integer, default=180
    )

    cabin_class: Mapped[str] = mapped_column(
        String(30), default="economy"
    )

    airline = relationship(
        "Airline",
        back_populates="flights",
    )

    aircraft = relationship(
        "Aircraft",
        back_populates="flights",
    )

    seats = relationship(
        "FlightSeat",
        back_populates="flight",
    )

    origin = relationship(
        "Airport",
        back_populates="departing_flights",
        foreign_keys=[origin_id],
    )

    destination = relationship(
        "Airport",
        back_populates="arriving_flights",
        foreign_keys=[destination_id],
    )
