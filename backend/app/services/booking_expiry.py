from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking, Flight, FlightSeat, Passenger, Payment


def release_booking(
    db: Session,
    booking_id: int,
    *,
    expire: bool = False,
    user_id: int | None = None,
):
    try:
        # Lock the booking to prevent two requests from releasing it.
        booking = db.scalar(
            select(Booking)
            .where(Booking.id == booking_id)
            .with_for_update()
        )

        if booking is None:
            raise HTTPException(404, "Booking not found.")

        # Customer cancellation requires ownership.
        # Background expiration does not require a user.
        if not expire and (
            user_id is None or booking.user_id != user_id
        ):
            raise HTTPException(404, "Booking not found.")

        if booking.status != "pending":
            raise HTTPException(
                409,
                f"Booking is already {booking.status}.",
            )

        # Lock the flight before changing inventory.
        flight = db.scalar(
            select(Flight)
            .where(Flight.id == booking.flight_id)
            .with_for_update()
        )

        if flight is None:
            raise HTTPException(404, "Flight not found.")

        if expire:
            if (
                booking.expires_at is None
                or booking.expires_at > datetime.now(timezone.utc)
            ):
                raise HTTPException(
                    409,
                    "Booking has not expired yet.",
                )

        if expire:
            existing_payment = db.scalar(
                select(Payment.id)
                .where(Payment.booking_id == booking.id)
                .limit(1)
            )

            if existing_payment is not None:
                raise HTTPException(
                    409,
                    "Payment reconciliation is required before expiration.",
                )

        # Do not release seats while payment may still be processing.
        # Applies to customer cancellation; expiration retains its
        # existing payment reconciliation checks.
        if not expire:
            active_payment = db.scalar(
                select(Payment.id)
                .where(
                    Payment.booking_id == booking.id,
                    Payment.status.in_(
                        ["created", "authorized", "captured"]
                    ),
                )
                .limit(1)
            )

            if active_payment is not None:
                raise HTTPException(
                    409,
                    "Payment is in progress or captured. "
                    "Cancellation requires payment reconciliation.",
                )

        # Release individually held seats within the booking transaction.
        assigned_passengers = db.scalars(
            select(Passenger)
            .where(
                Passenger.booking_id == booking.id,
                Passenger.flight_seat_id.is_not(None),
            )
            .order_by(Passenger.id)
            .with_for_update()
        ).all()

        if assigned_passengers:
            seat_ids = [
                passenger.flight_seat_id
                for passenger in assigned_passengers
            ]

            held_seats = db.scalars(
                select(FlightSeat)
                .where(
                    FlightSeat.id.in_(seat_ids),
                    FlightSeat.flight_id == flight.id,
                )
                .order_by(FlightSeat.id)
                .with_for_update()
            ).all()

            if (
                len(held_seats) != len(assigned_passengers)
                or any(seat.status != "held" for seat in held_seats)
            ):
                raise HTTPException(
                    409,
                    "Seat assignment conflict. Booking was not released.",
                )

            for passenger in assigned_passengers:
                passenger.flight_seat_id = None

            for seat in held_seats:
                seat.status = "available"

        flight.available_seats += booking.passenger_count

        booking.status = "expired" if expire else "cancelled"

        db.commit()
        db.refresh(booking)

        return {
            "booking_reference": booking.booking_reference,
            "status": booking.status,
            "released_seats": booking.passenger_count,
        }

    except Exception:
        db.rollback()
        raise


def expire_pending_bookings(db: Session):
    now = datetime.now(timezone.utc)

    expired_ids = db.scalars(
        select(Booking.id)
        .where(
            Booking.status == "pending",
            Booking.expires_at.is_not(None),
            Booking.expires_at <= now,
        )
        .order_by(Booking.id)
        .limit(100)
    ).all()

    released = 0

    for booking_id in expired_ids:
        try:
            release_booking(db, booking_id, expire=True)
            released += 1
        except HTTPException as exc:
            # Another worker may have processed this booking.
            if exc.status_code != 409:
                raise

    return {"expired_bookings": released}
