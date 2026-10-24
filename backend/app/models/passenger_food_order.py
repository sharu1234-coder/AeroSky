from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PassengerFoodOrder(Base):
    __tablename__ = "passenger_food_orders"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_passenger_food_quantity"),
        CheckConstraint("unit_price >= 0", name="ck_passenger_food_price"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    passenger_id: Mapped[int] = mapped_column(
        ForeignKey("passengers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    food_item_id: Mapped[int] = mapped_column(
        ForeignKey("food_items.id"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(default=1, nullable=False)

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    passenger = relationship("Passenger")
