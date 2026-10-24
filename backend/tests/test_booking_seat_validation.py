from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.schemas.booking import BookingCreate
from app.services.booking_service import create_booking


@pytest.mark.parametrize(
    "seat_numbers",
    [
        [None],
        ["1A", None],
    ],
)
def test_booking_rejects_missing_seat_selection(seat_numbers):
    flight = SimpleNamespace(
        id=101,
        departure_time=datetime.now(timezone.utc) + timedelta(days=30),
        available_seats=180,
        cabin_class="economy",
        price=Decimal("2500.00"),
    )

    db = MagicMock()
    db.scalar.return_value = flight

    passengers = [
        {
            "first_name": "Test",
            "last_name": "Passenger",
            "date_of_birth": "2000-01-01",
            "passenger_type": "adult",
            "seat_number": seat_number,
        }
        for seat_number in seat_numbers
    ]

    payload = BookingCreate(
        flight_id=101,
        contact_email="test@example.com",
        contact_phone="9876543210",
        passengers=passengers,
    )

    with pytest.raises(HTTPException) as exc:
        create_booking(db, payload, user_id=1)

    assert exc.value.status_code == 422
    assert "Select one seat for every passenger" in exc.value.detail

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
