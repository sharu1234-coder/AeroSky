
import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock

from app.services.payment_inspection import fetch_all_order_payments


def test_razorpay_api_failure():
    client = MagicMock()
    client.order.payments.side_effect = RuntimeError("API unavailable")

    with pytest.raises(HTTPException) as exc:
        fetch_all_order_payments(client, "order_test")

    assert exc.value.status_code == 502


def test_duplicate_payments_across_pages():
    client = MagicMock()

    first_page = [
        {"id": f"pay_{i}", "status": "failed"}
        for i in range(100)
    ]

    second_page = [
        {"id": "pay_0", "status": "captured"}
    ]

    client.order.payments.side_effect = [
        {"count": 100, "items": first_page},
        {"count": 1, "items": second_page},
    ]

    with pytest.raises(HTTPException) as exc:
        fetch_all_order_payments(client, "order_test")

    assert exc.value.status_code == 502


def test_invalid_collection_response():
    client = MagicMock()
    client.order.payments.return_value = {
        "count": 2,
        "items": [{"id": "pay_1"}],
    }

    with pytest.raises(HTTPException) as exc:
        fetch_all_order_payments(client, "order_test")

    assert exc.value.status_code == 502


def test_empty_payment_history():
    client = MagicMock()
    client.order.payments.return_value = {
        "count": 0,
        "items": [],
    }

    result = fetch_all_order_payments(client, "order_test")

    assert result == []
