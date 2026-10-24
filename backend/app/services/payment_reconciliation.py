from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking, Payment
from app.services.payment_inspection import inspect_booking_payments


def assess_booking_reconciliation(
    db: Session,
    booking_id: int,
) -> dict:
    booking = db.get(Booking, booking_id)

    if booking is None:
        return {
            "booking_id": booking_id,
            "decision": "not_found",
            "message": "Booking does not exist.",
        }

    if booking.status == "confirmed":
        return {
            "booking_id": booking.id,
            "decision": "already_confirmed",
            "message": "No reconciliation action required.",
        }

    if booking.status in ("cancelled", "expired"):
        inspection = inspect_booking_payments(db, booking.id)

        if inspection["captured_payments"] > 0:
            return {
                "booking_id": booking.id,
                "decision": "manual_reconciliation",
                "message": (
                    "Captured payment found for an inactive booking. "
                    "Review for reconciliation or refund."
                ),
                "inspection": inspection,
            }

        return {
            "booking_id": booking.id,
            "decision": "inactive",
            "message": (
                "Booking is already inactive. "
                "No automatic inventory changes permitted."
            ),
            "inspection": inspection,
        }

    if booking.status != "pending":
        return {
            "booking_id": booking.id,
            "decision": "manual_review",
            "message": "Unknown booking status.",
        }

    now = datetime.now(timezone.utc)

    if booking.expires_at is None:
        return {
            "booking_id": booking.id,
            "decision": "manual_review",
            "message": "Reservation expiration is missing.",
        }

    if booking.expires_at > now:
        return {
            "booking_id": booking.id,
            "decision": "still_active",
            "message": "Reservation has not expired.",
        }

    records = db.scalars(
        select(Payment)
        .where(Payment.booking_id == booking.id)
    ).all()

    if not records:
        return {
            "booking_id": booking.id,
            "decision": "eligible_for_expiration",
            "message": (
                "Reservation expired without a local payment order. "
                "The existing expiration worker may process it."
            ),
        }

    inspection = inspect_booking_payments(db, booking.id)

    if inspection["captured_payments"] > 0:
        return {
            "booking_id": booking.id,
            "decision": "manual_reconciliation",
            "message": (
                "Captured payment detected. "
                "Do not expire or confirm automatically."
            ),
            "inspection": inspection,
        }

    statuses = []

    for item in inspection["results"]:
        statuses.extend(item.get("razorpay_statuses", []))

        if item.get("razorpay_status") == "no_order":
            statuses.append("unknown")

    if "authorized" in statuses:
        decision = "payment_in_progress"
        message = "Authorized payment requires further verification."
    elif "mismatch" in statuses or "unknown" in statuses:
        decision = "manual_review"
        message = "Payment details require manual review."
    else:
        decision = "hold_for_recheck"
        message = (
            "No captured payment found in this inspection. "
            "Recheck later before any seat release."
        )

    return {
        "booking_id": booking.id,
        "decision": decision,
        "message": message,
        "inspection": inspection,
    }
