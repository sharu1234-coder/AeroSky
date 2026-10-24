import asyncio
import logging

from app.db.session import SessionLocal
from app.services.booking_expiry import expire_pending_bookings

logger = logging.getLogger(__name__)


async def booking_expiration_worker():
    logger.info("AeroSky booking expiration worker started.")

    while True:
        try:
            # Run synchronous SQLAlchemy operations outside the event loop.
            result = await asyncio.to_thread(process_expired_bookings)

            if result["expired_bookings"] > 0:
                logger.info(
                    "Automatically expired %s bookings.",
                    result["expired_bookings"],
                )

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception("Booking expiration worker failed.")

        await asyncio.sleep(30)


def process_expired_bookings():
    with SessionLocal() as db:
        return expire_pending_bookings(db)
