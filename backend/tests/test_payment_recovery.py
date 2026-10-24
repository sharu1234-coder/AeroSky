
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services.payment_recovery import get_payment_recovery_status


def check_recovery(booking_status, inspection):
    booking = SimpleNamespace(
        id=101,
        user_id=42,
        status=booking_status,
    )

    db = MagicMock()

    with (
        patch(
            "app.services.payment_recovery.require_owned_booking",
            return_value=booking,
        ),
        patch(
            "app.services.payment_recovery.inspect_booking_payments",
            return_value=inspection,
        ),
    ):
        result = get_payment_recovery_status(db, 101, 42)

    db.commit.assert_not_called()
    db.flush.assert_not_called()

    return result


def test_captured_payment_in_earlier_order():
    inspection = {
        "orders_checked": 2,
        "captured_payments": 1,
        "results": [
            {
                "local_status": "created",
                "razorpay_statuses": ["captured"],
            },
            {
                "local_status": "created",
                "razorpay_statuses": [],
            },
        ],
    }

    result = check_recovery("expired", inspection)

    assert result["recovery_status"] == "requires_reconciliation"
    assert result["payment_status"] == "captured"


def test_authorized_payment_requires_reconciliation():
    inspection = {
        "orders_checked": 1,
        "captured_payments": 0,
        "results": [
            {
                "local_status": "created",
                "razorpay_statuses": ["authorized"],
            },
        ],
    }

    result = check_recovery("pending", inspection)

    assert result["recovery_status"] == "requires_reconciliation"
    assert result["payment_status"] == "authorized"


def test_confirmed_booking_with_captured_payment():
    inspection = {
        "orders_checked": 1,
        "captured_payments": 1,
        "results": [
            {
                "local_status": "captured",
                "razorpay_statuses": ["captured"],
            },
        ],
    }

    result = check_recovery("confirmed", inspection)

    assert result["recovery_status"] == "confirmed"
    assert result["payment_status"] == "captured"
