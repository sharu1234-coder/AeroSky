
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services.payment_reconciliation import (
    assess_booking_reconciliation,
)


def test_expired_booking_with_captured_payment_requires_review():
    booking = SimpleNamespace(
        id=101,
        status="pending",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
    )

    db = MagicMock()
    db.get.return_value = booking
    db.scalars.return_value.all.return_value = [
        SimpleNamespace(id=201)
    ]

    inspection = {
        "booking_id": 101,
        "orders_checked": 1,
        "captured_payments": 1,
        "requires_reconciliation": True,
        "results": [
            {
                "payment_record_id": 201,
                "local_status": "created",
                "razorpay_statuses": ["captured"],
            }
        ],
    }

    with patch(
        "app.services.payment_reconciliation.inspect_booking_payments",
        return_value=inspection,
    ):
        result = assess_booking_reconciliation(db, 101)

    assert result["decision"] == "manual_reconciliation"
    db.commit.assert_not_called()
    db.flush.assert_not_called()


def test_expired_booking_with_authorized_payment_is_held():
    booking = SimpleNamespace(
        id=102,
        status="pending",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
    )

    db = MagicMock()
    db.get.return_value = booking
    db.scalars.return_value.all.return_value = [
        SimpleNamespace(id=202)
    ]

    inspection = {
        "booking_id": 102,
        "orders_checked": 1,
        "captured_payments": 0,
        "requires_reconciliation": False,
        "results": [
            {
                "payment_record_id": 202,
                "local_status": "created",
                "razorpay_statuses": ["authorized"],
            }
        ],
    }

    with patch(
        "app.services.payment_reconciliation.inspect_booking_payments",
        return_value=inspection,
    ):
        result = assess_booking_reconciliation(db, 102)

    assert result["decision"] == "payment_in_progress"
    db.commit.assert_not_called()
    db.flush.assert_not_called()
