from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.booking_expiry import release_booking


@pytest.mark.parametrize(
    "payment_status",
    ["created", "authorized", "captured", "failed", "refunded"],
)
def test_existing_payment_blocks_automatic_expiration(payment_status):
    booking = SimpleNamespace(
        id=101,
        user_id=42,
        flight_id=201,
        status="pending",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        passenger_count=1,
    )

    flight = SimpleNamespace(
        id=201,
        available_seats=179,
    )

    db = MagicMock()
    db.scalar.side_effect = [
        booking,
        flight,
        301,
    ]

    with pytest.raises(HTTPException) as exc:
        release_booking(db, booking_id=101, expire=True)

    assert exc.value.status_code == 409
    assert "reconciliation" in exc.value.detail.lower()

    assert booking.status == "pending"
    assert flight.available_seats == 179

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
    db.scalars.assert_not_called()


def test_expiration_query_does_not_filter_payment_status():
    from sqlalchemy import select
    from app.models import Payment

    query = (
        select(Payment.id)
        .where(Payment.booking_id == 101)
        .limit(1)
    )

    compiled = str(query.compile())

    assert "payments" in compiled.lower()
    assert "status" not in compiled.lower()
