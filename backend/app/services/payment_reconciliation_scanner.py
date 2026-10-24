import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking
from app.services.payment_reconciliation import (
    assess_booking_reconciliation,
)

logger = logging.getLogger(__name__)


def scan_expired_payment_bookings(
    db: Session,
    limit: int = 20,
) -> dict:
    now = datetime.now(timezone.utc)

    booking_ids = db.scalars(
        select(Booking.id)
        .where(
            Booking.status == "pending",
            Booking.expires_at.is_not(None),
            Booking.expires_at <= now,
        )
        .order_by(Booking.id)
        .limit(limit)
    ).all()

    results = []

    for booking_id in booking_ids:
        try:
            assessment = assess_booking_reconciliation(
                db,
                booking_id,
            )

            results.append({
                "booking_id": booking_id,
                "decision": assessment["decision"],
            })

        except Exception:
            db.rollback()

            logger.exception(
                "Reconciliation inspection failed for booking %s",
                booking_id,
            )

            results.append({
                "booking_id": booking_id,
                "decision": "inspection_failed",
            })

    return {
        "scanned": len(results),
        "results": results,
    }
