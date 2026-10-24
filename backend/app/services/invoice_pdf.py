from datetime import datetime, timedelta, timezone
from decimal import Decimal
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, HRFlowable, PageBreak,
)


NAVY = colors.HexColor("#10233F")
BLUE = colors.HexColor("#087EBC")
PALE = colors.HexColor("#EAF5FC")
MUTED = colors.HexColor("#60738A")
BORDER = colors.HexColor("#DCE7EF")
GREEN = colors.HexColor("#147D64")
IST = timezone(timedelta(hours=5, minutes=30))
MONEY = Decimal("0.01")


def safe(value):
    return escape(str(value if value is not None else "Not available"))


def money(value):
    return f"INR {Decimal(str(value)).quantize(MONEY):,.2f}"


def local_date(value):
    if not isinstance(value, datetime):
        return "Not available"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(IST).strftime("%d %b %Y, %I:%M %p IST")


def style(name, size=9, color=NAVY, bold=False, alignment=0):
    return ParagraphStyle(
        name,
        fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=size,
        leading=size * 1.5,
        textColor=color,
        alignment=alignment,
        spaceAfter=0,
    )


TITLE = style("invoice_title", 24, NAVY, True)
SUBTITLE = style("invoice_subtitle", 9, MUTED)
HEADING = style("invoice_heading", 11, NAVY, True)
BODY = style("invoice_body", 9)
SMALL = style("invoice_small", 8, MUTED)
BOLD = style("invoice_bold", 9, NAVY, True)
WHITE = style("invoice_white", 10, colors.white, True)
RIGHT = style("invoice_right", 9, NAVY, False, TA_RIGHT)
RIGHT_BOLD = style("invoice_right_bold", 9, NAVY, True, TA_RIGHT)


def P(value, paragraph_style=BODY):
    return Paragraph(safe(value), paragraph_style)


def section(story, title):
    story.append(Spacer(1, 7 * mm))
    story.append(P(title, HEADING))
    story.append(Spacer(1, 2 * mm))


def data_table(rows, widths, header=False):
    table = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, BORDER),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white, colors.HexColor("#F7FAFD")
            ]),
        ]
    table.setStyle(TableStyle(commands))
    return table


def generate_invoice_pdf(booking, food_orders, food_names, payment):
    """
    food_orders: list of PassengerFoodOrder ORM objects.
    food_names: dict mapping food_item_id to recorded item name.
    payment: captured Payment ORM object.
    """
    if booking.status != "confirmed" or payment.status != "captured":
        raise ValueError("Invoice requires a confirmed, captured booking.")

    passengers = sorted(booking.passengers, key=lambda p: p.id)
    passenger_by_id = {p.id: p for p in passengers}
    flight = booking.flight

    flight_fare = Decimal(str(flight.price)) * len(passengers)
    meal_total = sum(
        (Decimal(str(o.unit_price)) * o.quantity for o in food_orders),
        Decimal("0.00"),
    )
    booking_total = Decimal(str(booking.total_amount))
    paid_total = Decimal(payment.amount_paise) / Decimal(100)

    # Current flight prices can change after a booking. Never silently
    # produce a receipt whose line items fail to match the amount paid.
    if flight_fare + meal_total != booking_total:
        flight_fare = booking_total - meal_total

    if flight_fare < 0 or booking_total != paid_total:
        raise ValueError("Booking and captured payment totals do not reconcile.")

    base_per_passenger = (
        flight_fare / len(passengers) if passengers else Decimal("0.00")
    )

    buffer = BytesIO()
    width, height = A4
    usable = width - 38 * mm

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=19 * mm,
        leftMargin=19 * mm,
        topMargin=19 * mm,
        bottomMargin=19 * mm,
        title=f"AeroSky Demo Receipt - {booking.booking_reference}",
    )

    story = []

    heading = Table([
        [
            [
                P("AEROSKY", TITLE),
                P("PREMIUM BOOKING RECEIPT", SUBTITLE),
            ],
            [
                P("PAYMENT CAPTURED", style(
                    "captured_label", 11, GREEN, True, TA_RIGHT
                )),
                P("RAZORPAY TEST MODE", style(
                    "test_label", 8, MUTED, False, TA_RIGHT
                )),
            ],
        ]
    ], colWidths=[usable * 0.57, usable * 0.43])
    heading.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(heading)
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE))
    story.append(Spacer(1, 6 * mm))

    origin = flight.origin
    destination = flight.destination

    details = [
        [
            P("BOOKING REFERENCE", SMALL),
            P("BOOKING STATUS", SMALL),
        ],
        [
            P(booking.booking_reference, BOLD),
            P(booking.status.upper(), BOLD),
        ],
        [
            P("BOOKED ON", SMALL),
            P("PASSENGERS", SMALL),
        ],
        [
            P(local_date(booking.created_at)),
            P(str(booking.passenger_count)),
        ],
    ]
    story.append(data_table(details, [usable / 2, usable / 2]))

    section(story, "FLIGHT INFORMATION")
    route = f"{origin.code} ({origin.city})  TO  {destination.code} ({destination.city})"
    flight_rows = [
        [P("ROUTE", SMALL), P(route, BOLD)],
        [P("AIRLINE / FLIGHT", SMALL),
         P(f"{flight.airline.name} / {flight.flight_number}")],
        [P("DEPARTURE", SMALL), P(local_date(flight.departure_time))],
        [P("ARRIVAL", SMALL), P(local_date(flight.arrival_time))],
        [P("CABIN", SMALL), P(str(flight.cabin_class).title())],
    ]
    story.append(data_table(
        flight_rows, [usable * 0.30, usable * 0.70]
    ))

    section(story, "PASSENGERS & ASSIGNED SEATS")
    passenger_rows = [[
        P("PASSENGER", WHITE),
        P("TYPE", WHITE),
        P("SEAT", WHITE),
    ]]
    for passenger in passengers:
        seat = passenger.flight_seat
        passenger_rows.append([
            P(f"{passenger.first_name} {passenger.last_name}"),
            P(passenger.passenger_type.title()),
            P(seat.seat_number if seat else "Not assigned"),
        ])
    story.append(data_table(
        passenger_rows,
        [usable * 0.55, usable * 0.22, usable * 0.23],
        header=True,
    ))

    fare_start = len(story)
    section(story, "ITEMIZED FARE BREAKDOWN")
    fare_rows = [[
        P("DESCRIPTION", WHITE),
        P("QTY", WHITE),
        P("AMOUNT", WHITE),
    ]]

    fare_rows.append([
        P(f"Flight fare ({money(base_per_passenger)} per passenger)"),
        P(str(len(passengers))),
        P(money(flight_fare), RIGHT),
    ])

    for order in sorted(food_orders, key=lambda o: (o.passenger_id, o.id)):
        passenger = passenger_by_id.get(order.passenger_id)
        name = (
            f"{passenger.first_name} {passenger.last_name}"
            if passenger else "Passenger"
        )
        item = food_names.get(order.food_item_id, "Meal item")
        amount = Decimal(str(order.unit_price)) * order.quantity
        fare_rows.append([
            P(f"{item} - {name} ({money(order.unit_price)} each)"),
            P(str(order.quantity)),
            P(money(amount), RIGHT),
        ])

    if not food_orders:
        fare_rows.append([
            P("Meals - none selected"),
            P("-"),
            P(money(0), RIGHT),
        ])

    fare_rows.append([
        P("Seat selection - included"),
        P(str(len(passengers))),
        P(money(0), RIGHT),
    ])

    story.append(data_table(
        fare_rows,
        [usable * 0.67, usable * 0.09, usable * 0.24],
        header=True,
    ))

    story.append(Spacer(1, 5 * mm))
    totals = [
        [P("FLIGHT FARE", BOLD), P(money(flight_fare), RIGHT)],
        [P("MEALS TOTAL", BOLD), P(money(meal_total), RIGHT)],
        [P("ADDITIONAL CHARGES", BOLD), P(money(0), RIGHT)],
        [
            P("TOTAL PAID", style("total_label", 13, NAVY, True)),
            P(money(booking_total), style(
                "total_amount", 13, BLUE, True, TA_RIGHT
            )),
        ],
    ]
    total_table = data_table(totals, [usable * 0.65, usable * 0.35])
    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, -1), (-1, -1), PALE),
        ("TOPPADDING", (0, -1), (-1, -1), 12),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 12),
    ]))
    story.append(total_table)

    # Prevent fare items and the grand total from splitting apart.
    fare_content = story[fare_start:]
    story[fare_start:] = [KeepTogether(fare_content)]

    story.append(PageBreak())
    section(story, "PAYMENT DETAILS")
    payment_rows = [
        [P("PAYMENT STATUS", SMALL), P(payment.status.upper(), BOLD)],
        [P("PAYMENT ID", SMALL), P(payment.razorpay_payment_id)],
        [P("RAZORPAY ORDER ID", SMALL), P(payment.razorpay_order_id)],
        [P("AMOUNT CAPTURED", SMALL), P(money(paid_total), BOLD)],
        [P("PAYMENT RECORD UPDATED", SMALL),
         P(local_date(payment.updated_at))],
        [P("PAYMENT PROVIDER", SMALL), P("Razorpay (Test Mode)")],
        [P("PAYMENT METHOD", SMALL),
         P("Not stored in AeroSky payment records")],
    ]
    story.append(data_table(
        payment_rows, [usable * 0.38, usable * 0.62]
    ))

    section(story, "BOOKING CONTACT")
    story.append(P(f"Email: {booking.contact_email}"))
    story.append(P(f"Phone: {booking.contact_phone}"))

    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    story.append(Spacer(1, 3 * mm))
    story.append(P(
        "DEMO RECEIPT - NOT A VALID TAX INVOICE OR TRAVEL DOCUMENT",
        style("disclaimer", 9, colors.HexColor("#C62828"), True, TA_CENTER),
    ))
    story.append(P(
        "AeroSky is a portfolio demonstration. Payments use Razorpay "
        "Test Mode. No real airline ticket or financial transaction "
        "is issued.",
        style("disclaimer_body", 8, MUTED, False, TA_CENTER),
    ))

    def page_footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(BORDER)
        canvas.line(19 * mm, 14 * mm, width - 19 * mm, 14 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(19 * mm, 10 * mm, "AEROSKY | DEMO RECEIPT")
        canvas.drawRightString(
            width - 19 * mm, 10 * mm, f"Invoice page {doc.page}"
        )
        canvas.restoreState()

    document.build(
        story,
        onFirstPage=page_footer,
        onLaterPages=page_footer,
    )
    buffer.seek(0)
    return buffer.getvalue()
