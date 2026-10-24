import { getAccessToken } from "../lib/auth";
import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { CreditCard, Loader2, LockKeyhole } from "lucide-react";

import {
  loadRazorpay,
  openRazorpayCheckout,
  type RazorpayOrder,
  type RazorpaySuccess,
} from "../lib/razorpay";

interface PaymentButtonProps {
  bookingId: number;
  disabled?: boolean;
}

export default function PaymentButton({
  bookingId,
  disabled = false,
}: PaymentButtonProps) {
  const queryClient = useQueryClient();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [showRecovery, setShowRecovery] = useState(false);
  const [checkingRecovery, setCheckingRecovery] = useState(false);
  const [paymentUncertain, setPaymentUncertain] = useState(false);
  const [initialCheckPending, setInitialCheckPending] = useState(true);

  useEffect(() => {
    let active = true;
    const controller = new AbortController();

    async function checkExistingPayment() {
      try {
        const token = getAccessToken();

        if (!token) {
          if (active) {
            setPaymentUncertain(true);
            setMessage("Please log in to check your payment status.");
          }
          return;
        }

        const response = await fetch(
          `http://127.0.0.1:8000/api/v1/payments/recovery/${bookingId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          throw new Error("Unable to establish existing payment status.");
        }

        const data = await response.json();

        if (!active) return;

        if (data.recovery_status === "no_payment") {
          setPaymentUncertain(false);
        } else if (data.recovery_status === "confirmed") {
          setPaymentUncertain(true);
          setMessage("This booking is already confirmed.");
        } else {
          setPaymentUncertain(true);
          setShowRecovery(true);
          setMessage(
            "An existing payment order requires review. " +
            "Check Payment Status before attempting another payment."
          );
        }
      } catch {
        if (active) {
          setPaymentUncertain(true);
          setShowRecovery(true);
          setMessage(
            "Payment status could not be checked. " +
            "New payment attempts are temporarily disabled."
          );
        }
      } finally {
        if (active) {
          setInitialCheckPending(false);
        }
      }
    }

    void checkExistingPayment();

    return () => {
      active = false;
      controller.abort();
    };
  }, [bookingId]);

  async function verifyPayment(result: RazorpaySuccess) {
    setPaymentUncertain(true);
    setMessage("Verifying payment securely...");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/payments/verify",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getAccessToken()}`,
          },
          body: JSON.stringify({
            booking_id: bookingId,
            razorpay_order_id: result.razorpay_order_id,
            razorpay_payment_id: result.razorpay_payment_id,
            razorpay_signature: result.razorpay_signature,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Payment verification failed."
        );
      }

      if (
        data.booking_status !== "confirmed" ||
        data.payment_status !== "captured"
      ) {
        throw new Error(
          "Payment requires additional verification."
        );
      }

      setPaymentUncertain(false);
      setShowRecovery(false);
      setMessage("Test payment verified! Booking confirmed.");

      await queryClient.invalidateQueries({
        queryKey: ["booking", String(bookingId)],
      });
    } catch (error) {
      setShowRecovery(true);
      setMessage(
        (error instanceof Error ? error.message : "Verification failed.") +
        " Check payment status before attempting another payment."
      );
    } finally {
      setLoading(false);
    }
  }

  async function checkPaymentStatus() {
    if (checkingRecovery) return;

    setCheckingRecovery(true);

    try {
      const token = getAccessToken();

      if (!token) {
        throw new Error("Please log in to check your payment.");
      }

      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/payments/recovery/${bookingId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Unable to check payment status."
        );
      }

      if (data.recovery_status === "confirmed") {
        setPaymentUncertain(false);
        setMessage("Payment confirmed! Your booking is confirmed.");
        setShowRecovery(false);

        await queryClient.invalidateQueries({
          queryKey: ["booking", String(bookingId)],
        });
      } else if (data.recovery_status === "requires_reconciliation") {
        setMessage(
          "Razorpay reports a captured payment, but your booking " +
          "requires reconciliation. Do not pay again. Contact support."
        );
      } else if (data.recovery_status === "pending") {
        setMessage(
          "No matching captured payment was found yet. " +
          "Payment status may still change. Do not retry until resolved."
        );
      } else {
        setMessage(
          "Payment status: " + String(data.recovery_status) +
          ". Check your booking before paying."
        );
      }
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Unable to check payment status."
      );
    } finally {
      setCheckingRecovery(false);
    }
  }

  async function handlePayment() {
    if (loading || paymentUncertain || initialCheckPending) return;

    const token = getAccessToken();

    if (!token) {
      setMessage("Please log in before making a payment.");
      return;
    }

    setLoading(true);
    setMessage("");
    setShowRecovery(false);

    try {
      await loadRazorpay();

      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/payments/orders/${bookingId}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${getAccessToken()}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Unable to create payment order."
        );
      }

      const order = data as RazorpayOrder;

      // The backend is authoritative for booking expiration.
      // Do not open Checkout if its returned deadline has passed.
      const expirationValue = (
        order as RazorpayOrder & { expires_at?: string | null }
      ).expires_at;

      if (!expirationValue) {
        throw new Error(
          "Reservation expiration is unavailable. Please refresh the booking."
        );
      }

      const expiresAt = Date.parse(expirationValue);

      if (!Number.isFinite(expiresAt)) {
        throw new Error(
          "Invalid reservation expiration. Please refresh the booking."
        );
      }

      if (Date.now() >= expiresAt) {
        throw new Error(
          "Your reservation has expired. Please search for a new flight."
        );
      }

      openRazorpayCheckout(
        order,
        (result: RazorpaySuccess) => {
          void verifyPayment(result);
        },
        () => {
          setLoading(false);
          setPaymentUncertain(true);
          setShowRecovery(true);
          setMessage(
            "Checkout was closed. Your payment status may still be processing. " +
            "Check My Bookings before attempting another payment."
          );

          void queryClient.invalidateQueries({
            queryKey: ["booking", String(bookingId)],
          });
        }
      );
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Unable to open Razorpay Checkout."
      );
      setLoading(false);
    }
  }

  return (
    <div className="space-y-3">
      <button
        type="button"
        onClick={handlePayment}
        disabled={
          disabled ||
          loading ||
          paymentUncertain ||
          checkingRecovery ||
          initialCheckPending
        }
        className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-4 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : (
          <CreditCard className="h-5 w-5" />
        )}

        {loading || initialCheckPending
          ? "Checking..."
          : paymentUncertain
            ? "Payment Status Uncertain"
            : "Pay Securely"}
      </button>

      <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
        <LockKeyhole className="h-4 w-4" />
        Razorpay Test Mode — no real money charged
      </div>

      {showRecovery && (
        <button
          type="button"
          onClick={() => void checkPaymentStatus()}
          disabled={checkingRecovery || loading}
          className="w-full rounded-xl border border-blue-300 px-4 py-3 text-sm font-semibold text-blue-700 hover:bg-blue-50 disabled:opacity-50"
        >
          {checkingRecovery ? "Checking payment..." : "Check Payment Status"}
        </button>
      )}

      {message && (
        <p
          role="status"
          className="rounded-lg bg-blue-50 p-3 text-sm text-blue-800"
        >
          {message}
        </p>
      )}
    </div>
  );
}
