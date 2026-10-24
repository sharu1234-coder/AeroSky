from sqlalchemy.orm import Session

from app.services.booking_ownership import require_owned_booking
from app.services.payment_inspection import inspect_booking_payments


def get_payment_recovery_status(
    db: Session,
    booking_id: int,
    user_id: int,
):
    booking = require_owned_booking(db, booking_id, user_id)

    inspection = inspect_booking_payments(db, booking.id)

    if inspection["orders_checked"] == 0:
        return {
            "booking_id": booking.id,
            "booking_status": booking.status,
            "payment_status": "not_started",
            "recovery_status": "no_payment",
            "message": "No payment order exists for this booking.",
        }

    results = inspection["results"]

    local_statuses = [
        item.get("local_status")
        for item in results
    ]

    remote_statuses = []

    for item in results:
        if item.get("razorpay_status") == "no_order":
            remote_statuses.append("unknown")

        remote_statuses.extend(
            item.get("razorpay_statuses", [])
        )

    captured_found = (
        inspection["captured_payments"] > 0
        or "captured" in local_statuses
    )

    if captured_found:
        if booking.status == "confirmed":
            return {
                "booking_id": booking.id,
                "booking_status": booking.status,
                "payment_status": "captured",
                "recovery_status": "confirmed",
                "message": "Booking is confirmed.",
            }

        return {
            "booking_id": booking.id,
            "booking_status": booking.status,
            "payment_status": "captured",
            "recovery_status": "requires_reconciliation",
            "message": (
                "A captured payment was found for this booking. "
                "Do not pay again. Contact support for reconciliation."
            ),
        }

    if booking.status == "confirmed":
        return {
            "booking_id": booking.id,
            "booking_status": booking.status,
            "payment_status": "unknown",
            "recovery_status": "requires_reconciliation",
            "message": (
                "Booking is confirmed, but its captured payment "
                "could not be established. Contact support."
            ),
        }

    if (
        "authorized" in remote_statuses
        or "authorized" in local_statuses
    ):
        return {
            "booking_id": booking.id,
            "booking_status": booking.status,
            "payment_status": "authorized",
            "recovery_status": "requires_reconciliation",
            "message": (
                "A payment is authorized but not confirmed as captured. "
                "Do not pay again until its status is resolved."
            ),
        }

    if (
        "unknown" in remote_statuses
        or "mismatch" in remote_statuses
    ):
        return {
            "booking_id": booking.id,
            "booking_status": booking.status,
            "payment_status": "unknown",
            "recovery_status": "requires_reconciliation",
            "message": (
                "Payment records are incomplete or inconsistent. "
                "Do not pay again. Contact support."
            ),
        }

    return {
        "booking_id": booking.id,
        "booking_status": booking.status,
        "payment_status": local_statuses[-1],
        "recovery_status": "pending",
        "message": (
            "No matching captured payment was found during this check. "
            "Payment status may still change. Do not retry yet."
        ),
    }
