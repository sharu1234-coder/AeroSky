from io import BytesIO
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.graphics.barcode import code128


BLUE = colors.HexColor("#109BD0")
DARK = colors.HexColor("#14243A")
MUTED = colors.HexColor("#64748B")
LIGHT = colors.HexColor("#F2F8FC")
RED = colors.HexColor("#C62828")


def value(obj, *names, default=None):
    for name in names:
        result = getattr(obj, name, None) if obj is not None else None
        if result is not None:
            return result
    return default


def airport_code(airport):
    return str(value(airport, "iata_code", "code", default="---"))


def airport_name(airport):
    return str(value(airport, "city", "name", default="Not available"))


def fit(text, limit=32):
    text = str(text or "Not assigned")
    return text if len(text) <= limit else text[:limit - 3] + "..."


def label(c, x, y, text):
    c.setFont("Helvetica", 9)
    c.setFillColor(MUTED)
    c.drawString(x, y, text.upper())


def detail(c, x, y, title, content, limit=28):
    label(c, x, y, title)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(DARK)
    c.drawString(x, y - 20, fit(content, limit))


IST = timezone(timedelta(hours=5, minutes=30))


def local_datetime(dt):
    if not isinstance(dt, datetime):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST)


def date_text(dt):
    local = local_datetime(dt)
    return local.strftime("%d %b %Y") if local else "Not available"


def time_text(dt):
    local = local_datetime(dt)
    return local.strftime("%H:%M IST") if local else "Not available"


def generate_ticket_pdf(booking):
    buffer = BytesIO()
    page_w, page_h = landscape(A4)

    c = canvas.Canvas(buffer, pagesize=(page_w, page_h))
    c.setTitle(f"AeroSky Demo Boarding Pass - {booking.booking_reference}")

    flight = value(booking, "flight")
    origin = value(flight, "origin", "origin_airport")
    destination = value(flight, "destination", "destination_airport")
    airline = value(flight, "airline")

    departure = value(
        flight, "departure_time", "departure_datetime", "departure_at"
    )
    arrival = value(
        flight, "arrival_time", "arrival_datetime", "arrival_at"
    )

    origin_iata = airport_code(origin)
    destination_iata = airport_code(destination)

    flight_number = value(flight, "flight_number", default="Not available")
    airline_name = value(airline, "name", default="AeroSky Demo")

    passengers = list(value(booking, "passengers", default=[]) or [])
    if not passengers:
        passengers = [None] * max(1, int(booking.passenger_count))

    for index, passenger in enumerate(passengers, start=1):
        x, y = 35, 110
        w, h = page_w - 70, 365
        stub_x = x + w * 0.73

        # Ticket shadow and body
        c.setFillColor(colors.HexColor("#E2E8F0"))
        c.roundRect(x + 4, y - 5, w, h, 22, fill=1, stroke=0)

        c.setFillColor(colors.white)
        c.roundRect(x, y, w, h, 22, fill=1, stroke=0)

        # Blue top banner
        c.setFillColor(BLUE)
        c.roundRect(x, y + h - 66, w, 66, 20, fill=1, stroke=0)
        c.rect(x, y + h - 66, w, 35, fill=1, stroke=0)

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 23)
        c.drawString(x + 24, y + h - 43, "AEROSKY")

        c.setFont("Helvetica-Bold", 13)
        c.drawString(x + 235, y + h - 40, "BOARDING PASS")
        c.drawString(stub_x + 16, y + h - 40, "BOARDING PASS")

        # Perforated dividing line
        c.setStrokeColor(colors.HexColor("#CBD5E1"))
        c.setDash(5, 5)
        c.line(stub_x, y + 20, stub_x, y + h - 68)
        c.setDash()

        # Passenger name
        first = value(passenger, "first_name", default="")
        last = value(passenger, "last_name", default="")
        full_name = (str(first) + " " + str(last)).strip()
        if not full_name:
            full_name = "Passenger details unavailable"

        detail(c, x + 25, y + 260, "Passenger", full_name, 31)
        detail(c, x + 270, y + 260, "Flight", flight_number, 13)
        detail(c, x + 25, y + 230, "Airline", airline_name, 32)

        # Route
        c.setFont("Helvetica-Bold", 29)
        c.setFillColor(DARK)
        c.drawString(x + 25, y + 170, origin_iata)
        c.drawString(x + 275, y + 170, destination_iata)

        c.setStrokeColor(BLUE)
        c.setLineWidth(2)
        c.line(x + 125, y + 179, x + 250, y + 179)

        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(x + 177, y + 187, ">>>")

        c.setFont("Helvetica", 10)
        c.setFillColor(MUTED)
        c.drawString(x + 25, y + 150, fit(airport_name(origin), 19))
        c.drawString(x + 275, y + 150, fit(airport_name(destination), 19))

        detail(c, x + 25, y + 122, "Date", date_text(departure), 18)
        detail(c, x + 170, y + 122, "Departure", time_text(departure), 12)
        seat = value(passenger, "flight_seat")
        seat_number = value(
            seat, "seat_number", default="Not assigned"
        )
        detail(c, x + 305, y + 122, "Seat", seat_number, 13)

        detail(c, x + 25, y + 64, "Arrival", time_text(arrival), 18)
        detail(c, x + 170, y + 64, "Arrival Date", date_text(arrival), 18)
        detail(c, x + 305, y + 64, "Class",
               value(flight, "cabin_class", default="Not specified"), 15)

        # Right stub
        sx = stub_x + 16
        detail(c, sx, y + 260, "Passenger", full_name, 24)
        detail(c, sx, y + 207, "From", origin_iata, 12)
        detail(c, sx + 85, y + 207, "To", destination_iata, 12)
        detail(c, sx, y + 152, "Flight", flight_number, 15)
        detail(c, sx, y + 112, "Date", date_text(departure), 18)
        detail(c, sx, y + 67, "Status", booking.status.upper(), 15)

        # Machine-readable demo reference (not an airline boarding credential)
        barcode_data = f"DEMO-{booking.id}-{index}"
        barcode = code128.Code128(
            barcode_data,
            barHeight=34,
            barWidth=0.7,
            humanReadable=False,
        )
        barcode.drawOn(c, sx, y + 12)

        # Clear invalid-for-travel labeling
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(
            page_w / 2,
            78,
            "DEMO BOARDING PASS - NOT VALID FOR TRAVEL",
        )

        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        c.drawCentredString(
            page_w / 2,
            60,
            "Razorpay Test Mode | No real airline ticket issued",
        )
        c.drawCentredString(
            page_w / 2,
            44,
            f"Booking: {booking.booking_reference}  |  "
            f"Passenger {index} of {len(passengers)}  |  "
            f"Fare: INR {booking.total_amount}",
        )

        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
