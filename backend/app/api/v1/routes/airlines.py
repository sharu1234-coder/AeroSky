from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Airline
from app.schemas.flight import AirlineResponse


router = APIRouter(prefix="/airlines", tags=["Airlines"])


@router.get("", response_model=list[AirlineResponse])
def list_airlines(db: Session = Depends(get_db)):
    query = select(Airline).order_by(Airline.name)

    return db.scalars(query).all()
