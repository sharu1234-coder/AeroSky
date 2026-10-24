from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import (
    Booking,
    User,
    Passenger,
    Payment,
    PassengerFoodOrder,
    FoodItem,
)
from app.services.ticket_pdf import generate_ticket_pdf
from app.services.invoice_pdf import generate_invoice_pdf
from pypdf import PdfReader, PdfWriter


router = APIRouter(
    prefix="/bookings",
    tags=["Tickets"],
)


@router.get("/{booking_id}/ticket")
def download_demo_ticket(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.scalar(
        select(Booking)
        .options(
            selectinload(Booking.passengers).selectinload(
                Passenger.flight_seat
            ),
            selectinload(Booking.flight),
        )
        .where(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
        )
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )

    if booking.status != "confirmed":
        raise HTTPException(
            status_code=409,
            detail="E-ticket is available only for confirmed bookings.",
        )

    # Existing boarding pass generator remains unchanged.
    ticket_bytes = generate_ticket_pdf(booking)

    # Use only a successfully captured payment.
    payment = db.scalar(
        select(Payment)
        .where(
            Payment.booking_id == booking.id,
            Payment.status == "captured",
        )
        .order_by(Payment.id.desc())
    )

    if payment is None:
        raise HTTPException(
            status_code=409,
            detail="Captured payment not found for this booking.",
        )

    passenger_ids = [passenger.id for passenger in booking.passengers]

    food_orders = (
        db.scalars(
            select(PassengerFoodOrder)
            .where(
                PassengerFoodOrder.passenger_id.in_(passenger_ids)
            )
            .order_by(PassengerFoodOrder.id)
        ).all()
        if passenger_ids
        else []
    )

    food_ids = {order.food_item_id for order in food_orders}

    food_names = {}

    if food_ids:
        food_items = db.scalars(
            select(FoodItem).where(FoodItem.id.in_(food_ids))
        ).all()

        food_names = {
            item.id: item.name
            for item in food_items
        }

    # Create the separate premium payment receipt.
    invoice_bytes = generate_invoice_pdf(
        booking=booking,
        food_orders=food_orders,
        food_names=food_names,
        payment=payment,
    )

    # Preserve all existing boarding-pass pages, then append invoice.
    writer = PdfWriter()

    ticket_reader = PdfReader(BytesIO(ticket_bytes))
    invoice_reader = PdfReader(BytesIO(invoice_bytes))

    for page in ticket_reader.pages:
        writer.add_page(page)

    for page in invoice_reader.pages:
        writer.add_page(page)

    output = BytesIO()
    writer.write(output)

    pdf_bytes = output.getvalue()

    filename = f"AeroSky-{booking.booking_reference}.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
