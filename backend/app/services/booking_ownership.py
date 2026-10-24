from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking


def require_owned_booking(
    db: Session,
    booking_id: int,
    user_id: int,
) -> Booking:
    booking = db.scalar(
        select(Booking).where(
            Booking.id == booking_id,
            Booking.user_id == user_id,
        )
    )

    if booking is None:
        raise HTTPException(404, "Booking not found.")

    return booking
