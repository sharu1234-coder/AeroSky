from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.booking_expiry import release_booking


def test_captured_payment_blocks_booking_expiration():
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
        booking,  # Locked booking
        flight,   # Locked flight
        301,      # Existing payment requiring reconciliation
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


def test_expiration_guard_includes_captured_payment():
    from pathlib import Path

    source = Path(
        "app/services/booking_expiry.py"
    ).read_text(encoding="utf-8")

    assert "Payment.booking_id == booking.id" in source
    expiration_guard = source.split("if expire:", 2)[2].split("if not expire:", 1)[0]
    assert "Payment.status.in_" not in expiration_guard
