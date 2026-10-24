from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services.payment_confirmation import confirm_payment
from app.schemas.payment import PaymentVerifyRequest


def test_payment_confirmation_rejects_incomplete_seats():
    booking = SimpleNamespace(
        id=101,
        user_id=42,
        booking_reference="ASK-TEST123",
        flight_id=201,
        passenger_count=2,
        status="pending",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    payment = SimpleNamespace(
        id=301,
        booking_id=101,
        razorpay_order_id="order_test123",
        razorpay_payment_id=None,
        amount_paise=500000,
        currency="INR",
        status="created",
    )

    db = MagicMock()
    db.scalar.side_effect = [payment, booking, payment]
    db.scalars.return_value.all.return_value = [
        SimpleNamespace(id=401, flight_seat_id=501)
    ]

    payload = PaymentVerifyRequest(
        booking_id=101,
        razorpay_order_id="order_test123",
        razorpay_payment_id="pay_test123",
        razorpay_signature="test_signature",
    )

    with (
        patch(
            "app.services.booking_ownership.require_owned_booking",
            return_value=booking,
        ),
        patch(
            "app.services.payment_confirmation.verify_checkout_signature",
        ),
        patch(
            "app.services.payment_confirmation.verify_captured_payment",
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            confirm_payment(db, payload, user_id=42)

    assert exc.value.status_code == 409
    assert "seat assignments are incomplete" in exc.value.detail
    assert booking.status == "pending"
    assert payment.status == "created"
    db.commit.assert_not_called()
    db.rollback.assert_called()
