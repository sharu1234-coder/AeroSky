from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Airport, Airline, Flight


AIRPORTS = [
    ("HYD", "Rajiv Gandhi International Airport", "Hyderabad", "India"),
    ("DEL", "Indira Gandhi International Airport", "Delhi", "India"),
    ("BOM", "Chhatrapati Shivaji Maharaj International Airport", "Mumbai", "India"),
    ("BLR", "Kempegowda International Airport", "Bengaluru", "India"),
    ("MAA", "Chennai International Airport", "Chennai", "India"),
    ("CCU", "Netaji Subhas Chandra Bose International Airport", "Kolkata", "India"),
    ("GOX", "Manohar International Airport", "Goa", "India"),
    ("COK", "Cochin International Airport", "Kochi", "India"),
    ("DXB", "Dubai International Airport", "Dubai", "UAE"),
    ("SIN", "Singapore Changi Airport", "Singapore", "Singapore"),
]

AIRLINES = [
    ("6E", "IndiGo"),
    ("AI", "Air India"),
    ("QP", "Akasa Air"),
    ("EK", "Emirates"),
    ("SQ", "Singapore Airlines"),
]

ROUTES = [
    ("6E", "6E-201", "HYD", "DEL", 120, "4899.00"),
    ("AI", "AI-540", "HYD", "BOM", 95, "5299.00"),
    ("QP", "QP-142", "HYD", "BLR", 75, "3199.00"),
    ("6E", "6E-611", "HYD", "MAA", 70, "2899.00"),
    ("AI", "AI-760", "DEL", "HYD", 125, "5099.00"),
    ("6E", "6E-332", "BOM", "HYD", 90, "4599.00"),
    ("EK", "EK-527", "HYD", "DXB", 230, "18999.00"),
    ("SQ", "SQ-519", "HYD", "SIN", 270, "23999.00"),
    ("6E", "6E-804", "BLR", "GOX", 85, "3999.00"),
    ("AI", "AI-901", "DEL", "CCU", 130, "5999.00"),
    ("6E", "6E-721", "MAA", "COK", 80, "3299.00"),
    ("QP", "QP-350", "BOM", "DEL", 125, "5499.00"),
]


def seed():
    with SessionLocal() as db:
        for code, name, city, country in AIRPORTS:
            airport = db.scalar(
                select(Airport).where(Airport.code == code)
            )
            if airport is None:
                db.add(Airport(
                    code=code,
                    name=name,
                    city=city,
                    country=country,
                ))

        for code, name in AIRLINES:
            airline = db.scalar(
                select(Airline).where(Airline.code == code)
            )
            if airline is None:
                db.add(Airline(code=code, name=name))

        db.commit()

        airports = {
            airport.code: airport
            for airport in db.scalars(select(Airport)).all()
        }

        airlines = {
            airline.code: airline
            for airline in db.scalars(select(Airline)).all()
        }

        now = datetime.now(timezone.utc)

        count = 0

        for day_offset in range(1, 15):
            for index, route in enumerate(ROUTES):
                airline_code, number, origin, destination, minutes, price = route

                departure = (
                    now + timedelta(days=day_offset)
                ).replace(
                    hour=3 + (index % 12),
                    minute=0,
                    second=0,
                    microsecond=0,
                )

                exists = db.scalar(
                    select(Flight).where(
                        Flight.flight_number == number,
                        Flight.departure_time == departure,
                    )
                )

                if exists:
                    continue

                flight = Flight(
                    flight_number=number,
                    airline_id=airlines[airline_code].id,
                    origin_id=airports[origin].id,
                    destination_id=airports[destination].id,
                    departure_time=departure,
                    arrival_time=departure + timedelta(minutes=minutes),
                    price=Decimal(price),
                    available_seats=180,
                    cabin_class="economy",
                )

                db.add(flight)
                count += 1

        db.commit()

        print("AeroSky database seeded successfully!")
        print(f"New demo flights created: {count}")


if __name__ == "__main__":
    seed()
