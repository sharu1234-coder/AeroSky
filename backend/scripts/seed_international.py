from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Airport, Airline, Aircraft, Flight, FlightSeat


ROUTES = [
    ("6E", "6E-1801", "HYD", "AUH", 230, "15999.00"),
    ("6E", "6E-1802", "HYD", "DOH", 260, "16999.00"),
    ("6E", "6E-1803", "HYD", "MCT", 210, "13999.00"),
    ("6E", "6E-1804", "DEL", "KTM", 110, "8999.00"),
    ("6E", "6E-1805", "MAA", "CMB", 85, "7999.00"),
    ("6E", "6E-1806", "BLR", "BKK", 225, "18999.00"),
]


def seed():
    with SessionLocal() as db:
        airports = {
            airport.code: airport
            for airport in db.scalars(select(Airport)).all()
        }

        airlines = {
            airline.code: airline
            for airline in db.scalars(select(Airline)).all()
        }

        aircraft = db.scalar(
            select(Aircraft).where(Aircraft.model == "A320-ECO")
        )

        if aircraft is None:
            raise RuntimeError("A320-ECO aircraft not found.")

        if aircraft.total_seats != 180:
            raise RuntimeError("Expected aircraft capacity of 180.")

        required_airports = {
            code
            for route in ROUTES
            for code in (route[2], route[3])
        }

        missing = required_airports - airports.keys()

        if missing:
            raise RuntimeError(f"Missing airports: {sorted(missing)}")

        if "6E" not in airlines:
            raise RuntimeError("IndiGo airline record not found.")

        created = 0
        skipped = 0
        today = datetime.now(timezone.utc).date()

        for day_offset in range(1, 15):
            departure_date = today + timedelta(days=day_offset)

            for index, route in enumerate(ROUTES):
                airline_code, number, origin, destination, minutes, price = route

                departure = datetime(
                    departure_date.year,
                    departure_date.month,
                    departure_date.day,
                    5 + index,
                    0,
                    tzinfo=timezone.utc,
                )

                existing = db.scalar(
                    select(Flight.id).where(
                        Flight.flight_number == number,
                        Flight.departure_time == departure,
                    )
                )

                if existing is not None:
                    skipped += 1
                    continue

                flight = Flight(
                    flight_number=number,
                    airline_id=airlines[airline_code].id,
                    aircraft_id=aircraft.id,
                    origin_id=airports[origin].id,
                    destination_id=airports[destination].id,
                    departure_time=departure,
                    arrival_time=departure + timedelta(minutes=minutes),
                    price=Decimal(price),
                    available_seats=180,
                    cabin_class="economy",
                )

                db.add(flight)
                db.flush()

                for row in range(1, 31):
                    for column in "ABCDEF":
                        db.add(
                            FlightSeat(
                                flight_id=flight.id,
                                seat_number=f"{row}{column}",
                                seat_row=row,
                                seat_column=column,
                                cabin_class="economy",
                                status="available",
                            )
                        )

                created += 1

        db.commit()

        print("\n=== INTERNATIONAL FLIGHT SEED ===")
        print("New flights:", created)
        print("Existing flights skipped:", skipped)
        print("New seats:", created * 180)
        print("SUCCESS")


if __name__ == "__main__":
    seed()
