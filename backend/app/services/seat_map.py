from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Aircraft, Flight, FlightSeat


def get_flight_seat_map(db: Session, flight_id: int) -> dict:
    flight = db.get(Flight, flight_id)

    if flight is None:
        raise HTTPException(
            status_code=404,
            detail="Flight not found.",
        )

    if flight.aircraft_id is None:
        raise HTTPException(
            status_code=409,
            detail="Seat map is not configured for this flight.",
        )

    aircraft = db.get(Aircraft, flight.aircraft_id)

    if aircraft is None:
        raise HTTPException(
            status_code=409,
            detail="Aircraft configuration is missing.",
        )

    seats = db.scalars(
        select(FlightSeat)
        .where(FlightSeat.flight_id == flight_id)
        .order_by(FlightSeat.seat_row, FlightSeat.seat_column)
    ).all()

    if not seats:
        raise HTTPException(
            status_code=409,
            detail="No seats configured for this flight.",
        )

    return {
        "flight_id": flight.id,
        "flight_number": flight.flight_number,
        "aircraft": {
            "name": aircraft.name,
            "model": aircraft.model,
            "total_seats": aircraft.total_seats,
        },
        "available_seats": sum(
            seat.status == "available" for seat in seats
        ),
        "seats": [
            {
                "seat_number": seat.seat_number,
                "row": seat.seat_row,
                "column": seat.seat_column,
                "cabin_class": seat.cabin_class,
                "status": seat.status,
            }
            for seat in seats
        ],
    }
