from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking, FlightSeat, Passenger, Payment
from app.schemas.payment import PaymentVerifyRequest
from app.services.payment_verification import (
    verify_checkout_signature,
    verify_captured_payment,
)


def confirm_payment(db: Session, payload: PaymentVerifyRequest, user_id: int):
    from app.services.booking_ownership import require_owned_booking

    # Reject requests for bookings not owned by this user.
    require_owned_booking(db, payload.booking_id, user_id)

    # First verify the Checkout signature.
    verify_checkout_signature(
        payload.razorpay_order_id,
        payload.razorpay_payment_id,
        payload.razorpay_signature,
    )

    # Read the expected amount and order from our database.
    payment = db.scalar(
        select(Payment).where(
            Payment.booking_id == payload.booking_id,
            Payment.razorpay_order_id == payload.razorpay_order_id,
        )
    )

    if payment is None:
        raise HTTPException(404, "Payment order not found.")

    # Independently verify the captured payment with Razorpay.
    verify_captured_payment(
        payload.razorpay_order_id,
        payload.razorpay_payment_id,
        payment.amount_paise,
        payment.currency,
    )

    # Finish the read transaction before acquiring locks.
    db.rollback()

    try:
        # Lock booking first, matching the expiration worker's order.
        booking = db.scalar(
            select(Booking)
            .where(
                Booking.id == payload.booking_id,
                Booking.user_id == user_id,
            )
            .with_for_update()
        )

        if booking is None:
            raise HTTPException(404, "Booking not found.")

        payment = db.scalar(
            select(Payment)
            .where(
                Payment.booking_id == booking.id,
                Payment.razorpay_order_id == payload.razorpay_order_id,
            )
            .with_for_update()
        )

        if payment is None:
            raise HTTPException(404, "Payment record not found.")

        if (
            payment.razorpay_payment_id is not None
            and payment.razorpay_payment_id
            != payload.razorpay_payment_id
        ):
            raise HTTPException(
                409,
                "This order is associated with another payment.",
            )

        if payment.status == "captured" and booking.status == "confirmed":
            result = {
                "booking_id": booking.id,
                "booking_reference": booking.booking_reference,
                "booking_status": booking.status,
                "payment_status": payment.status,
                "razorpay_payment_id": payment.razorpay_payment_id,
                "confirmed_at": None,
            }
            db.commit()
            return result

        now = datetime.now(timezone.utc)

        if (
            booking.status != "pending"
            or booking.expires_at is None
            or booking.expires_at <= now
        ):
            raise HTTPException(
                409,
                "Reservation is no longer active. "
                "Captured payment requires reconciliation or refund.",
            )

        # Finalize held passenger seats in the same transaction
        # as the booking and payment confirmation.
        assigned_passengers = db.scalars(
            select(Passenger)
            .where(
                Passenger.booking_id == booking.id,
                Passenger.flight_seat_id.is_not(None),
            )
            .order_by(Passenger.id)
            .with_for_update()
        ).all()

        if len(assigned_passengers) != booking.passenger_count:
            raise HTTPException(
                409,
                "Passenger seat assignments are incomplete. "
                "Payment requires reconciliation.",
            )

        if assigned_passengers:
            seat_ids = [
                passenger.flight_seat_id
                for passenger in assigned_passengers
            ]

            held_seats = db.scalars(
                select(FlightSeat)
                .where(
                    FlightSeat.id.in_(seat_ids),
                    FlightSeat.flight_id == booking.flight_id,
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
                    "Seat assignment conflict. Payment requires reconciliation.",
                )

            for seat in held_seats:
                seat.status = "booked"

        payment.razorpay_payment_id = payload.razorpay_payment_id
        payment.status = "captured"
        booking.status = "confirmed"

        result = {
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "booking_status": booking.status,
            "payment_status": payment.status,
            "razorpay_payment_id": payment.razorpay_payment_id,
            "confirmed_at": now,
        }

        db.commit()
        return result

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            500,
            "Payment confirmation could not be completed.",
        )
