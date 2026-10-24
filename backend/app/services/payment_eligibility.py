from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking


def check_payment_eligibility(db: Session, booking_id: int):
    booking = db.scalar(
        select(Booking).where(Booking.id == booking_id)
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )

    now = datetime.now(timezone.utc)

    if booking.status != "pending":
        return {
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "eligible": False,
            "reason": f"Booking status is {booking.status}.",
            "total_amount": str(booking.total_amount),
            "currency": booking.currency,
            "expires_at": booking.expires_at,
        }

    if booking.expires_at is None or booking.expires_at <= now:
        return {
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "eligible": False,
            "reason": "Reservation has expired.",
            "total_amount": str(booking.total_amount),
            "currency": booking.currency,
            "expires_at": booking.expires_at,
        }

    return {
        "booking_id": booking.id,
        "booking_reference": booking.booking_reference,
        "eligible": True,
        "reason": "Booking is eligible for payment.",
        "total_amount": str(booking.total_amount),
        "currency": booking.currency,
        "expires_at": booking.expires_at,
    }
