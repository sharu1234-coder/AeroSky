import asyncio
from contextlib import asynccontextmanager

from app.workers.booking_expiration import booking_expiration_worker

from app.api.v1.router import api_router


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(booking_expiration_worker())

    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan,
    title="AeroSky API",
    description="Production-oriented Flight Booking and Travel Management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/", tags=["System"])
def root():
    return {
        "application": "AeroSky API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "aerosky-backend",
    }


app.include_router(api_router)
