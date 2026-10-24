from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import Booking, User
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import create_booking, get_booking
from app.services.booking_expiry import (
    release_booking,
    expire_pending_bookings,
)


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_booking(
        db,
        payload,
        user_id=current_user.id,
    )


@router.get(
    "/my",
    response_model=list[BookingResponse],
)
def retrieve_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.booking_service import get_user_bookings

    return get_user_bookings(
        db,
        user_id=current_user.id,
    )


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def retrieve_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_booking(
        db,
        booking_id,
        user_id=current_user.id,
    )


@router.post("/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Confirm ownership before changing booking state.
    # release_booking performs its own row locking.
    owned_booking = db.get(Booking, booking_id)

    if (
        owned_booking is None
        or owned_booking.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )

    db.rollback()

    return release_booking(
        db,
        booking_id,
        user_id=current_user.id,
    )


@router.post("/maintenance/expire", include_in_schema=False)
def expire_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(
        status_code=403,
        detail="Maintenance is handled by the background worker.",
    )
