from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from secrets import token_hex

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Booking, Flight, FlightSeat, Passenger
from app.models.food_item import FoodItem
from app.models.passenger_food_order import PassengerFoodOrder
from app.schemas.booking import BookingCreate


def calculate_age(birth_date: date, travel_date: date) -> int:
    return (
        travel_date.year
        - birth_date.year
        - (
            (travel_date.month, travel_date.day)
            < (birth_date.month, birth_date.day)
        )
    )


def create_booking(db: Session, payload: BookingCreate, user_id: int) -> Booking:
    try:
        # PostgreSQL row lock prevents concurrent seat overselling.
        flight = db.scalar(
            select(Flight)
            .where(Flight.id == payload.flight_id)
            .with_for_update()
        )

        if flight is None:
            raise HTTPException(
                status_code=404,
                detail="Flight not found.",
            )

        if flight.departure_time <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=400,
                detail="This flight has already departed.",
            )

        passenger_count = len(payload.passengers)

        if flight.available_seats < passenger_count:
            raise HTTPException(
                status_code=409,
                detail="Not enough seats available.",
            )

        # Demo booking rules:
        # Adult: 12 years and older on travel date.
        # Child: 2 through 11 years on travel date.
        # Infants under 2 are not yet supported.
        travel_date = flight.departure_time.date()

        for passenger in payload.passengers:
            age = calculate_age(passenger.date_of_birth, travel_date)

            if passenger.passenger_type == "adult" and age < 12:
                raise HTTPException(
                    status_code=422,
                    detail="Adult passengers must be at least 12 years old.",
                )

            if passenger.passenger_type == "child" and not 2 <= age < 12:
                raise HTTPException(
                    status_code=422,
                    detail="Child passengers must be 2 to 11 years old.",
                )

        # Validate requested seats while holding the flight row lock.
        requested_numbers = [
            item.seat_number
            for item in payload.passengers
            if item.seat_number is not None
        ]

        if len(requested_numbers) != passenger_count:
            raise HTTPException(
                status_code=422,
                detail="Select one seat for every passenger.",
            )

        if len(set(requested_numbers)) != len(requested_numbers):
            raise HTTPException(
                status_code=422,
                detail="Each passenger must select a different seat.",
            )

        selected_seats = {}

        if requested_numbers:
            seats = db.scalars(
                select(FlightSeat)
                .where(
                    FlightSeat.flight_id == flight.id,
                    FlightSeat.seat_number.in_(requested_numbers),
                )
                .with_for_update()
            ).all()

            selected_seats = {
                seat.seat_number: seat
                for seat in seats
            }

            if len(selected_seats) != passenger_count:
                raise HTTPException(
                    status_code=422,
                    detail="One or more selected seats do not exist on this flight.",
                )

            for seat in selected_seats.values():
                if seat.status != "available":
                    raise HTTPException(
                        status_code=409,
                        detail=f"Seat {seat.seat_number} is no longer available.",
                    )

                if seat.cabin_class != flight.cabin_class:
                    raise HTTPException(
                        status_code=422,
                        detail="Selected seat does not match the flight cabin class.",
                    )

        # Never accept a price from the client.
        # Demo fare: same base fare for adults and children.
        flight_total = (
            Decimal(flight.price) * Decimal(passenger_count)
        ).quantize(Decimal("0.01"))

        requested_food_ids = [
            food_id
            for passenger in payload.passengers
            for food_id in passenger.food_item_ids
        ]

        for passenger in payload.passengers:
            if len(passenger.food_item_ids) != len(set(passenger.food_item_ids)):
                raise HTTPException(
                    status_code=422,
                    detail="Duplicate food items are not allowed for a passenger.",
                )

        food_items = {}

        if requested_food_ids:
            items = db.scalars(
                select(FoodItem).where(
                    FoodItem.id.in_(set(requested_food_ids)),
                    FoodItem.is_available.is_(True),
                )
            ).all()

            food_items = {item.id: item for item in items}

            if len(food_items) != len(set(requested_food_ids)):
                raise HTTPException(
                    status_code=422,
                    detail="One or more selected food items are unavailable.",
                )

        food_total = sum(
            (
                Decimal(food_items[food_id].price)
                for passenger in payload.passengers
                for food_id in passenger.food_item_ids
            ),
            Decimal("0.00"),
        )

        total_amount = (flight_total + food_total).quantize(
            Decimal("0.01")
        )

        reference = "ASK-" + token_hex(6).upper()

        booking = Booking(
            user_id=user_id,
            booking_reference=reference,
            flight_id=flight.id,
            passenger_count=passenger_count,
            total_amount=total_amount,
            currency="INR",
            status="pending",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
            contact_email=str(payload.contact_email),
            contact_phone=payload.contact_phone,
        )

        for item in payload.passengers:
            assigned_seat = (
                selected_seats.get(item.seat_number)
                if item.seat_number
                else None
            )

            if assigned_seat is not None:
                assigned_seat.status = "held"

            saved_passenger = Passenger(
                first_name=item.first_name,
                last_name=item.last_name,
                date_of_birth=item.date_of_birth,
                passenger_type=item.passenger_type,
                flight_seat=assigned_seat,
            )

            booking.passengers.append(saved_passenger)

            for food_id in item.food_item_ids:
                db.add(
                    PassengerFoodOrder(
                        passenger=saved_passenger,
                        food_item_id=food_id,
                        quantity=1,
                        unit_price=food_items[food_id].price,
                    )
                )

        # Reserve seats within the same transaction.
        flight.available_seats -= passenger_count

        db.add(booking)
        db.commit()

        saved = db.scalar(
            select(Booking)
            .options(selectinload(Booking.passengers))
            .where(Booking.id == booking.id)
        )

        return saved

    except Exception:
        db.rollback()
        raise


def get_booking(
    db: Session,
    booking_id: int,
    user_id: int,
) -> Booking:
    booking = db.scalar(
        select(Booking)
        .options(
                selectinload(Booking.passengers),
                selectinload(Booking.flight).selectinload(Flight.origin),
                selectinload(Booking.flight).selectinload(Flight.destination),
                selectinload(Booking.flight).selectinload(Flight.airline),
            )
        .where(
            Booking.id == booking_id,
            Booking.user_id == user_id,
        )
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )

    return booking



def get_user_bookings(
    db: Session,
    user_id: int,
) -> list[Booking]:
    return list(
        db.scalars(
            select(Booking)
            .options(
                selectinload(Booking.passengers),
                selectinload(Booking.flight).selectinload(Flight.origin),
                selectinload(Booking.flight).selectinload(Flight.destination),
                selectinload(Booking.flight).selectinload(Flight.airline),
            )
            .where(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc(), Booking.id.desc())
        ).all()
    )
