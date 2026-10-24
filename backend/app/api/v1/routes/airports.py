from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Airport
from app.schemas.flight import AirportResponse


router = APIRouter(prefix="/airports", tags=["Airports"])


@router.get("", response_model=list[AirportResponse])
def list_airports(
    search: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
):
    query = select(Airport)

    if search and search.strip():
        term = f"%{search.strip()}%"

        query = query.where(
            or_(
                Airport.code.ilike(term),
                Airport.city.ilike(term),
                Airport.name.ilike(term),
                Airport.country.ilike(term),
            )
        )

    query = query.order_by(Airport.city).limit(50)

    return db.scalars(query).all()
