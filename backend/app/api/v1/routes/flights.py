from datetime import date, datetime, time, timedelta, timezone
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Airport, Flight
from app.schemas.flight import FlightResponse
from app.services.seat_map import get_flight_seat_map


router = APIRouter(prefix="/flights", tags=["Flights"])

INDIA_TIMEZONE = timezone(timedelta(hours=5, minutes=30))


@router.get("/search", response_model=list[FlightResponse])
def search_flights(
    origin: str = Query(min_length=3, max_length=3),
    destination: str = Query(min_length=3, max_length=3),
    departure_date: date = Query(),
    passengers: int = Query(default=1, ge=1, le=9),
    cabin_class: Literal[
        "economy", "premium_economy", "business", "first"
    ] = "economy",
    sort_by: Literal[
        "price", "departure", "duration"
    ] = "price",
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    origin = origin.upper()
    destination = destination.upper()

    if origin == destination:
        raise HTTPException(
            status_code=400,
            detail="Origin and destination must be different.",
        )

    if departure_date < datetime.now(INDIA_TIMEZONE).date():
        raise HTTPException(
            status_code=400,
            detail="Departure date cannot be in the past.",
        )

    start_local = datetime.combine(
        departure_date,
        time.min,
        tzinfo=INDIA_TIMEZONE,
    )

    end_local = start_local + timedelta(days=1)

    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)

    query = (
        select(Flight)
        .join(Airport, Flight.origin_id == Airport.id)
        .where(
            Airport.code == origin,
            Flight.departure_time >= start_utc,
            Flight.departure_time < end_utc,
            Flight.available_seats >= passengers,
            Flight.cabin_class == cabin_class,
            Flight.destination.has(Airport.code == destination),
        )
        .options(
            joinedload(Flight.airline),
            joinedload(Flight.origin),
            joinedload(Flight.destination),
        )
    )

    flights = db.scalars(query).all()

    if sort_by == "price":
        flights.sort(key=lambda flight: flight.price)

    elif sort_by == "departure":
        flights.sort(key=lambda flight: flight.departure_time)

    elif sort_by == "duration":
        flights.sort(
            key=lambda flight: (
                flight.arrival_time - flight.departure_time
            ).total_seconds()
        )

    return flights[:limit]

@router.get("/{flight_id}/seats")
def retrieve_flight_seats(
    flight_id: int,
    db: Session = Depends(get_db),
):
    return get_flight_seat_map(db, flight_id)
