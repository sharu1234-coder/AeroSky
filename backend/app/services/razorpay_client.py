import os

import razorpay
from dotenv import load_dotenv

load_dotenv()


def get_razorpay_client():
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")

    if not key_id or not key_secret:
        raise RuntimeError("Razorpay credentials are missing.")

    if not key_id.startswith("rzp_test_"):
        raise RuntimeError("Only Razorpay Test Mode is allowed.")

    return razorpay.Client(auth=(key_id, key_secret))
