from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import (
    Airline, Airport, Booking, Flight,
    FlightSeat, Passenger, User,
)
from app.schemas.booking import BookingCreate
from app.services.booking_service import create_booking


def test_two_customers_cannot_book_same_seat():
    source_url = make_url(settings.DATABASE_URL)

    if source_url.get_backend_name() != "postgresql":
        pytest.fail("PostgreSQL is required.")

    if source_url.database != "aerosky_test":
        pytest.fail(
            "SAFETY STOP: Set DATABASE_URL to aerosky_test "
            "before running this test."
        )

    engine = create_engine(
        source_url,
        connect_args={"connect_timeout": 5},
    )
    Session = sessionmaker(bind=engine, expire_on_commit=False)

    unique = uuid4().hex[:8].upper()
    flight_id = None

    try:
        with Session.begin() as db:
            actual_database = db.scalar(
                text("SELECT current_database()")
            )
            assert actual_database == "aerosky_test"

            airline = Airline(
                code="Q" + unique[:2],
                name=f"Concurrency Test {unique}",
            )
            origin = Airport(
                code="R" + unique[:2],
                name="Test Origin",
                city="Test City A",
                country="India",
            )
            destination = Airport(
                code="S" + unique[:2],
                name="Test Destination",
                city="Test City B",
                country="India",
            )

            db.add_all([airline, origin, destination])
            db.flush()

            flight = Flight(
                flight_number=f"CT-{unique}",
                airline_id=airline.id,
                origin_id=origin.id,
                destination_id=destination.id,
                departure_time=(
                    datetime.now(timezone.utc)
                    + timedelta(days=30)
                ),
                arrival_time=(
                    datetime.now(timezone.utc)
                    + timedelta(days=30, hours=2)
                ),
                price=Decimal("2500.00"),
                available_seats=1,
                cabin_class="economy",
            )
            db.add(flight)
            db.flush()

            flight_id = flight.id

            seat = FlightSeat(
                flight_id=flight_id,
                seat_number="1A",
                seat_row=1,
                seat_column="A",
                cabin_class="economy",
                status="available",
            )
            db.add(seat)

            users = [
                User(
                    email=f"{unique.lower()}-{i}@example.com",
                    hashed_password="test-only-not-a-real-password",
                    full_name=f"Test Customer {i}",
                )
                for i in (1, 2)
            ]
            db.add_all(users)
            db.flush()
            user_ids = [user.id for user in users]

        barrier = Barrier(2)

        def attempt_booking(user_id):
            payload = BookingCreate(
                flight_id=flight_id,
                contact_email=f"customer{user_id}@example.com",
                contact_phone="9876543210",
                passengers=[
                    {
                        "first_name": "Test",
                        "last_name": "Passenger",
                        "date_of_birth": date(2000, 1, 1),
                        "passenger_type": "adult",
                        "seat_number": "1A",
                    }
                ],
            )

            with Session() as db:
                barrier.wait(timeout=10)

                try:
                    booking = create_booking(
                        db,
                        payload,
                        user_id=user_id,
                    )
                    return ("success", booking.id)

                except HTTPException as exc:
                    return ("conflict", exc.status_code)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(attempt_booking, user_id)
                for user_id in user_ids
            ]
            results = [
                future.result(timeout=20)
                for future in futures
            ]

        with Session() as db:
            flight = db.get(Flight, flight_id)

            seat = db.scalar(
                select(FlightSeat).where(
                    FlightSeat.flight_id == flight_id,
                    FlightSeat.seat_number == "1A",
                )
            )

            booking_count = db.scalar(
                select(func.count(Booking.id)).where(
                    Booking.flight_id == flight_id
                )
            )

            passenger_count = db.scalar(
                select(func.count(Passenger.id)).where(
                    Passenger.flight_seat_id == seat.id
                )
            )

            print("\n=== CONCURRENCY TEST RESULTS ===")
            print("Request results:", results)
            print("Bookings created:", booking_count)
            print("Seat status:", seat.status)
            print("Passengers assigned to seat:", passenger_count)
            print("Available seats:", flight.available_seats)

            assert sorted(results, key=str) == [
                ("conflict", 409),
                ("success", next(
                    value for status, value in results
                    if status == "success"
                )),
            ]
            assert booking_count == 1
            assert seat.status == "held"
            assert passenger_count == 1
            assert flight.available_seats == 0

            print(
                "SUCCESS: Double booking prevented "
                "by PostgreSQL transaction locking."
            )

    finally:
        if flight_id is not None:
            with Session.begin() as cleanup_db:
                cleanup_db.execute(
                    text("""
                        DELETE FROM passengers
                        WHERE booking_id IN (
                            SELECT id FROM bookings
                            WHERE flight_id = :flight_id
                        )
                    """),
                    {"flight_id": flight_id},
                )

                cleanup_db.execute(
                    text(
                        "DELETE FROM bookings "
                        "WHERE flight_id = :flight_id"
                    ),
                    {"flight_id": flight_id},
                )

                cleanup_db.execute(
                    text(
                        "DELETE FROM flight_seats "
                        "WHERE flight_id = :flight_id"
                    ),
                    {"flight_id": flight_id},
                )

                cleanup_db.execute(
                    text(
                        "DELETE FROM flights "
                        "WHERE id = :flight_id"
                    ),
                    {"flight_id": flight_id},
                )

                cleanup_db.execute(
                    text(
                        "DELETE FROM users "
                        "WHERE email LIKE :pattern"
                    ),
                    {"pattern": unique.lower() + "-%@example.com"},
                )

                cleanup_db.execute(
                    text(
                        "DELETE FROM airlines WHERE code = :code"
                    ),
                    {"code": "Q" + unique[:2]},
                )

                cleanup_db.execute(
                    text(
                        "DELETE FROM airports "
                        "WHERE code IN (:origin, :destination)"
                    ),
                    {
                        "origin": "R" + unique[:2],
                        "destination": "S" + unique[:2],
                    },
                )

        engine.dispose()
