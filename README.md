# AeroSky - Full-Stack Flight Booking Application

AeroSky is a full-stack flight booking web application built with React, TypeScript, FastAPI, and PostgreSQL.

> Portfolio demonstration project. Razorpay payments operate in Test Mode. No real flight tickets are issued.

## Features

- Search domestic and international flights
- User registration and JWT authentication
- Interactive aircraft seat selection
- Passenger information management
- Passenger-wise meal ordering
- Automatic fare calculation
- Razorpay Test Mode payment integration
- Booking confirmation and booking history
- Downloadable PDF boarding passes
- Premium PDF invoices with detailed fare breakdowns
- Seat reservation and booking expiration safeguards

## Technology Stack

| Component | Technology |
| --- | --- |
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT |
| Payments | Razorpay Test Mode |
| PDF Generation | ReportLab, pypdf |
| Testing | Pytest |

## Project Structure

- `backend/` - FastAPI application, database models, migrations and tests
- `frontend/` - React and TypeScript user interface
- `docs/` - Project documentation
- `infrastructure/` - Infrastructure configuration

## Local Development

### Backend

1. Navigate to the `backend` directory.
2. Create and activate a Python virtual environment.
3. Install dependencies using `pip install -r requirements.txt`.
4. Configure `.env` using `.env.example` with your own local settings.
5. Apply database migrations using `alembic upgrade head`.
6. Start the API using `uvicorn app.main:app --reload`.

API documentation: http://localhost:8000/docs

### Frontend

1. Navigate to the `frontend` directory.
2. Install dependencies using `npm install`.
3. Start the development server using `npm run dev`.

Frontend URL: http://localhost:5173

## Booking Workflow

1. Search for flights.
2. Select a flight and enter passenger details.
3. Choose seats and optional meals.
4. Review the complete fare.
5. Complete a simulated payment.
6. View the confirmed booking.
7. Download the boarding pass and payment invoice.

## Screenshots

Application screenshots will be added here.

## Disclaimer

AeroSky is an educational portfolio project and is not affiliated with any airline. All booking and payment workflows are demonstrations.
