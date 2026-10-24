from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AirportResponse(BaseModel):
    id: int
    code: str
    name: str
    city: str
    country: str

    model_config = ConfigDict(from_attributes=True)


class AirlineResponse(BaseModel):
    id: int
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class FlightResponse(BaseModel):
    id: int
    flight_number: str
    airline: AirlineResponse
    origin: AirportResponse
    destination: AirportResponse
    departure_time: datetime
    arrival_time: datetime
    price: Decimal = Field(ge=0)
    available_seats: int
    cabin_class: str

    model_config = ConfigDict(from_attributes=True)
