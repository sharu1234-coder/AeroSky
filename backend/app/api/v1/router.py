from app.api.v1.routes import food
from fastapi import APIRouter

from app.api.v1.routes import airports, airlines, flights, bookings


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(airports.router)
api_router.include_router(airlines.router)
api_router.include_router(flights.router)

api_router.include_router(bookings.router)



from app.api.v1.routes import payments

api_router.include_router(payments.router)


from app.api.v1.routes import tickets

api_router.include_router(tickets.router)


from app.api.v1.routes import auth

api_router.include_router(auth.router)

api_router.include_router(food.router)
