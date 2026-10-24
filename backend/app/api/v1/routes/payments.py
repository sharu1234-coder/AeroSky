from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.payment import (
    PaymentVerifyRequest,
    PaymentConfirmationResponse,
)
from app.services.booking_ownership import require_owned_booking
from app.services.payment_eligibility import check_payment_eligibility
from app.services.payment_order import create_payment_order
from app.services.payment_confirmation import confirm_payment
from app.services.payment_recovery import get_payment_recovery_status


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.get("/eligibility/{booking_id}")
def payment_eligibility(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_owned_booking(db, booking_id, current_user.id)

    return check_payment_eligibility(db, booking_id)


@router.post("/orders/{booking_id}")
def create_razorpay_order(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_payment_order(
        db,
        booking_id,
        user_id=current_user.id,
    )


@router.post(
    "/verify",
    response_model=PaymentConfirmationResponse,
)
def verify_razorpay_payment(
    payload: PaymentVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return confirm_payment(
        db,
        payload,
        user_id=current_user.id,
    )


@router.get("/recovery/{booking_id}")
def payment_recovery_status(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_payment_recovery_status(
        db,
        booking_id,
        current_user.id,
    )
