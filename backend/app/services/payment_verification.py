from fastapi import HTTPException

from app.services.razorpay_client import get_razorpay_client


def verify_checkout_signature(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
) -> None:
    client = get_razorpay_client()

    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid Razorpay payment signature.",
        )


def verify_captured_payment(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    expected_amount: int,
    expected_currency: str = "INR",
) -> dict:
    client = get_razorpay_client()

    try:
        payment = client.payment.fetch(razorpay_payment_id)
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve payment from Razorpay.",
        )

    if payment.get("order_id") != razorpay_order_id:
        raise HTTPException(
            status_code=400,
            detail="Payment order ID mismatch.",
        )

    if payment.get("amount") != expected_amount:
        raise HTTPException(
            status_code=400,
            detail="Payment amount mismatch.",
        )

    if payment.get("currency") != expected_currency:
        raise HTTPException(
            status_code=400,
            detail="Payment currency mismatch.",
        )

    if payment.get("status") != "captured":
        raise HTTPException(
            status_code=409,
            detail="Payment has not been captured.",
        )

    return payment
