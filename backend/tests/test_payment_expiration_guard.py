
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services.payment_order import create_payment_order


@pytest.mark.parametrize(
    "status,expires_offset",
    [
        ("expired", -5),
        ("cancelled", 5),
        ("confirmed", 5),
        ("pending", -5),
    ],
)
def test_invalid_booking_cannot_create_payment_order(
    status,
    expires_offset,
):
    booking = SimpleNamespace(
        id=101,
        user_id=42,
        status=status,
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=expires_offset)
        ),
        total_amount=5000,
        currency="INR",
    )

    db = MagicMock()
    db.scalar.return_value = booking

    with patch(
        "app.services.payment_order.get_razorpay_client"
    ) as mock_client:
        with pytest.raises(HTTPException) as exc:
            create_payment_order(
                db,
                booking_id=101,
                user_id=42,
            )

        assert exc.value.status_code in (400, 404, 409)
        mock_client.assert_not_called()
