from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PaymentVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    booking_id: int = Field(gt=0)
    razorpay_order_id: str = Field(min_length=1, max_length=100)
    razorpay_payment_id: str = Field(min_length=1, max_length=100)
    razorpay_signature: str = Field(min_length=1, max_length=512)


class PaymentConfirmationResponse(BaseModel):
    booking_id: int
    booking_reference: str
    booking_status: str
    payment_status: str
    razorpay_payment_id: str
    confirmed_at: datetime | None = None
