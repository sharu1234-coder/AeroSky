from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services.payment_order import create_payment_order


@pytest.mark.parametrize(
    "payment_status",
    ["captured", "failed", "refunded"],
)
def test_existing_payment_history_blocks_new_order(payment_status):
    booking = SimpleNamespace(
        id=101,
        user_id=42,
        status="pending",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        total_amount=Decimal("2500.00"),
        booking_reference="ASK-TEST123",
    )

    previous_payment = SimpleNamespace(
        id=301,
        booking_id=101,
        status=payment_status,
    )

    db = MagicMock()
    db.scalar.side_effect = [
        booking,
        None,
        previous_payment.id,
    ]

    with patch(
        "app.services.payment_order.get_razorpay_client"
    ) as razorpay_client:
        with pytest.raises(HTTPException) as exc:
            create_payment_order(db, booking_id=101, user_id=42)

        assert exc.value.status_code == 409
        assert "reconciliation" in exc.value.detail.lower()

        razorpay_client.assert_not_called()

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_existing_created_order_is_reused():
    booking = SimpleNamespace(
        id=101,
        user_id=42,
        status="pending",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    existing_payment = SimpleNamespace(
        id=301,
        razorpay_order_id="order_existing123",
        amount_paise=250000,
        currency="INR",
    )

    db = MagicMock()
    db.scalar.side_effect = [booking, existing_payment]

    with patch(
        "app.services.payment_order.get_razorpay_client"
    ) as razorpay_client:
        result = create_payment_order(db, booking_id=101, user_id=42)

        razorpay_client.assert_not_called()

    assert result["razorpay_order_id"] == "order_existing123"
    assert result["amount"] == 250000

    db.commit.assert_not_called()
