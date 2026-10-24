from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Aircraft, Flight, FlightSeat
from scripts.seed import ROUTES as ORIGINAL_ROUTES
from scripts.seed_international import ROUTES as INTERNATIONAL_ROUTES


ROUTES = ORIGINAL_ROUTES + INTERNATIONAL_ROUTES
FLIGHTS_PER_ROUTE = 12
DAYS = 14

# UTC departure hours; all flights remain within their UTC calendar date.
DEPARTURE_HOURS = list(range(0, 24, 2))


def seed():
    with SessionLocal() as db:
        aircraft = db.scalar(
            select(Aircraft).where(Aircraft.model == "A320-ECO")
        )

        if aircraft is None or aircraft.total_seats != 180:
            raise RuntimeError("Expected A320-ECO aircraft with 180 seats.")

        # Resolve existing airports and airlines without changing their records.
        from app.models import Airport, Airline

        airports = {
            item.code: item.id
            for item in db.scalars(select(Airport)).all()
        }
        airlines = {
            item.code: item.id
            for item in db.scalars(select(Airline)).all()
        }

        for airline_code, _, origin, destination, _, _ in ROUTES:
            if airline_code not in airlines:
                raise RuntimeError(f"Missing airline: {airline_code}")
            if origin not in airports or destination not in airports:
                raise RuntimeError(f"Missing route airports: {origin}-{destination}")

        today = datetime.now(timezone.utc).date()
        created = 0
        skipped = 0

        for day_offset in range(1, DAYS + 1):
            day = today + timedelta(days=day_offset)

            for route_index, route in enumerate(ROUTES):
                airline_code, _, origin, destination, duration, base_price = route

                for slot in range(FLIGHTS_PER_ROUTE):
                    india_timezone = timezone(timedelta(hours=5, minutes=30))

                    local_departure = datetime(
                        day.year, day.month, day.day,
                        DEPARTURE_HOURS[slot], 0,
                        tzinfo=india_timezone,
                    )

                    departure = local_departure.astimezone(timezone.utc)

                    # Unique flight number for each route and departure slot.
                    flight_number = (
                        f"{airline_code}-D{route_index + 1:02d}"
                        f"{slot + 1:02d}"
                    )

                    exists = db.scalar(
                        select(Flight.id).where(
                            Flight.flight_number == flight_number,
                            Flight.departure_time == departure,
                        )
                    )

                    if exists is not None:
                        skipped += 1
                        continue

                    # Modest fare variation for comparison in the UI.
                    price = Decimal(base_price) + Decimal(slot * 175)

                    flight = Flight(
                        flight_number=flight_number,
                        airline_id=airlines[airline_code],
                        aircraft_id=aircraft.id,
                        origin_id=airports[origin],
                        destination_id=airports[destination],
                        departure_time=departure,
                        arrival_time=departure + timedelta(minutes=duration),
                        price=price,
                        available_seats=180,
                        cabin_class="economy",
                    )

                    db.add(flight)
                    db.flush()

                    db.add_all([
                        FlightSeat(
                            flight_id=flight.id,
                            seat_number=f"{row}{column}",
                            seat_row=row,
                            seat_column=column,
                            cabin_class="economy",
                            status="available",
                        )
                        for row in range(1, 31)
                        for column in "ABCDEF"
                    ])

                    created += 1

            db.commit()
            print(
                f"Day {day_offset}/{DAYS}: "
                f"created {created}, skipped {skipped}",
                flush=True,
            )

        print("\n=== MULTI-FLIGHT SEED COMPLETE ===")
        print("New flights:", created)
        print("Existing generated flights skipped:", skipped)
        print("New seats:", created * 180)


if __name__ == "__main__":
    seed()
