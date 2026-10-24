from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Airport(Base):
    __tablename__ = "airports"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    city: Mapped[str] = mapped_column(String(100), index=True)
    country: Mapped[str] = mapped_column(String(100))

    departing_flights = relationship(
        "Flight",
        back_populates="origin",
        foreign_keys="Flight.origin_id",
    )

    arriving_flights = relationship(
        "Flight",
        back_populates="destination",
        foreign_keys="Flight.destination_id",
    )
