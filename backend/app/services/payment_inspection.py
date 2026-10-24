from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Payment
from app.services.razorpay_client import get_razorpay_client


def fetch_all_order_payments(client, order_id: str) -> list:
    all_items = []
    skip = 0
    page_size = 100
    seen_ids = set()
    max_pages = 100

    for _ in range(max_pages):
        try:
            response = client.order.payments(
                order_id,
                {"count": page_size, "skip": skip},
            )
        except Exception:
            raise HTTPException(
                status_code=502,
                detail="Unable to retrieve Razorpay payment history.",
            )

        if not isinstance(response, dict):
            raise HTTPException(
                status_code=502,
                detail="Invalid Razorpay response.",
            )

        items = response.get("items")
        reported_count = response.get("count")

        if (
            not isinstance(items, list)
            or not isinstance(reported_count, int)
            or isinstance(reported_count, bool)
            or reported_count != len(items)
            or len(items) > page_size
        ):
            raise HTTPException(
                status_code=502,
                detail="Inconsistent Razorpay payment page.",
            )

        for item in items:
            if not isinstance(item, dict):
                raise HTTPException(
                    status_code=502,
                    detail="Invalid Razorpay payment record.",
                )

            payment_id = item.get("id")

            if not isinstance(payment_id, str) or not payment_id:
                raise HTTPException(
                    status_code=502,
                    detail="Razorpay payment ID is missing.",
                )

            if payment_id in seen_ids:
                raise HTTPException(
                    status_code=502,
                    detail="Duplicate payment found across pages.",
                )

            seen_ids.add(payment_id)
            all_items.append(item)

        if len(items) < page_size:
            return all_items

        skip += len(items)

    raise HTTPException(
        status_code=502,
        detail="Razorpay payment history exceeded inspection limit.",
    )


def inspect_booking_payments(db: Session, booking_id: int) -> dict:
    records = db.scalars(
        select(Payment)
        .where(Payment.booking_id == booking_id)
        .order_by(Payment.id)
    ).all()

    if not records:
        return {
            "booking_id": booking_id,
            "orders_checked": 0,
            "captured_payments": 0,
            "requires_reconciliation": False,
            "results": [],
        }

    client = get_razorpay_client()
    results = []
    captured_count = 0

    for record in records:
        if not record.razorpay_order_id:
            results.append({
                "payment_record_id": record.id,
                "local_status": record.status,
                "razorpay_status": "no_order",
            })
            continue

        items = fetch_all_order_payments(
            client,
            record.razorpay_order_id,
        )

        statuses = []

        for item in items:
            if not isinstance(item, dict):
                raise HTTPException(
                    status_code=502,
                    detail="Invalid Razorpay payment item.",
                )

            matches = (
                item.get("order_id") == record.razorpay_order_id
                and item.get("amount") == record.amount_paise
                and item.get("currency") == record.currency
            )

            if not matches:
                statuses.append("mismatch")
                continue

            status = item.get("status", "unknown")
            statuses.append(status)

            if status == "captured":
                captured_count += 1

        results.append({
            "payment_record_id": record.id,
            "local_status": record.status,
            "razorpay_statuses": statuses,
        })

    return {
        "booking_id": booking_id,
        "orders_checked": len(records),
        "captured_payments": captured_count,
        "requires_reconciliation": captured_count > 0,
        "results": results,
    }
