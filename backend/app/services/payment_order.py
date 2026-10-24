import os
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking, Payment
from app.services.razorpay_client import get_razorpay_client


def create_payment_order(db: Session, booking_id: int, user_id: int):
    try:
        booking = db.scalar(
            select(Booking)
            .where(
                Booking.id == booking_id,
                Booking.user_id == user_id,
            )
            .with_for_update()
        )

        if booking is None:
            raise HTTPException(404, "Booking not found.")

        if booking.status != "pending":
            raise HTTPException(
                409,
                f"Booking is {booking.status}; payment is unavailable.",
            )

        now = datetime.now(timezone.utc)

        if booking.expires_at is None or booking.expires_at <= now:
            raise HTTPException(
                409,
                "Booking reservation has expired.",
            )

        existing = db.scalar(
            select(Payment)
            .where(
                Payment.booking_id == booking.id,
                Payment.status.in_(["created", "authorized"]),
            )
            .order_by(Payment.id.desc())
        )

        if existing and existing.razorpay_order_id:
            return {
                "payment_id": existing.id,
                "booking_id": booking.id,
                "razorpay_order_id": existing.razorpay_order_id,
                "amount": existing.amount_paise,
                "currency": existing.currency,
                "key_id": os.getenv("RAZORPAY_KEY_ID"),
                "expires_at": booking.expires_at,
            }

        previous_payment = db.scalar(
            select(Payment.id)
            .where(Payment.booking_id == booking.id)
            .limit(1)
        )

        if previous_payment is not None:
            raise HTTPException(
                409,
                "Existing payment history requires reconciliation. "
                "Do not create another payment order.",
            )

        amount = int(
            (Decimal(str(booking.total_amount)) * 100)
            .to_integral_value()
        )

        if amount <= 0:
            raise HTTPException(400, "Invalid booking amount.")

        client = get_razorpay_client()

        order = client.order.create(
            {
                "amount": amount,
                "currency": "INR",
                "receipt": f"booking_{booking.id}",
                "notes": {
                    "booking_reference": booking.booking_reference,
                },
            }
        )

        payment = Payment(
            booking_id=booking.id,
            razorpay_order_id=order["id"],
            amount_paise=amount,
            currency="INR",
            status="created",
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        return {
            "payment_id": payment.id,
            "booking_id": booking.id,
            "razorpay_order_id": payment.razorpay_order_id,
            "amount": payment.amount_paise,
            "currency": payment.currency,
            "key_id": os.getenv("RAZORPAY_KEY_ID"),
            "expires_at": booking.expires_at,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=502,
            detail="Unable to create payment order.",
        )
