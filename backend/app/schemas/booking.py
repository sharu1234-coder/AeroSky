from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class PassengerCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    passenger_type: Literal["adult", "child"]
    seat_number: str | None = Field(
        default=None,
        min_length=2,
        max_length=10,
        pattern=r"^[1-9][0-9]*[A-Z]{1,2}$",
    )


    @field_validator("first_name", "last_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value or not all(
            character.isalpha() or character in " '-"
            for character in value
        ):
            raise ValueError("Enter a valid passenger name.")
        return value
    food_item_ids: list[int] = Field(default_factory=list, max_length=10)


class BookingCreate(BaseModel):
    flight_id: int = Field(gt=0)
    contact_email: EmailStr
    contact_phone: str = Field(
        min_length=10,
        max_length=20,
        pattern=r"^\+?[0-9]{10,15}$",
    )
    passengers: list[PassengerCreate] = Field(
        min_length=1,
        max_length=9,
    )


class PassengerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    passenger_type: str

    model_config = ConfigDict(from_attributes=True)


class AirportSummary(BaseModel):
    code: str
    city: str

    model_config = ConfigDict(from_attributes=True)


class AirlineSummary(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class FlightSummary(BaseModel):
    flight_number: str
    departure_time: datetime
    arrival_time: datetime
    origin: AirportSummary
    destination: AirportSummary
    airline: AirlineSummary

    model_config = ConfigDict(from_attributes=True)


class BookingResponse(BaseModel):
    id: int
    booking_reference: str
    flight_id: int
    flight: FlightSummary
    passenger_count: int
    total_amount: Decimal
    currency: str
    status: str
    contact_email: str
    contact_phone: str
    expires_at: datetime | None
    created_at: datetime
    passengers: list[PassengerResponse]

    model_config = ConfigDict(from_attributes=True)
