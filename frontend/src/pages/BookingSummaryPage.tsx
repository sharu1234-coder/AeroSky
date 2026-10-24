import { downloadBookingTicket } from "../lib/ticketDownload";
import PaymentButton from "../components/PaymentButton";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  CalendarClock,
  CheckCircle2,
  Clock3,
  Plane,
  ShieldCheck,
} from "lucide-react";
import { apiGet } from "../lib/api";

type Booking = {
  id: number;
  booking_reference: string;
  flight_id: number;
  passenger_count: number;
  total_amount: string;
  currency: string;
  status: string;
  expires_at: string | null;
  created_at: string;
};

function formatRemaining(milliseconds: number) {
  const seconds = Math.max(0, Math.ceil(milliseconds / 1000));
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  return `${String(minutes).padStart(2, "0")}:${String(
    remainingSeconds
  ).padStart(2, "0")}`;
}

export default function BookingSummaryPage() {
  const navigate = useNavigate();
  const { bookingId } = useParams();
  const queryClient = useQueryClient();

  const [now, setNow] = useState(Date.now());
  const [downloadingTicket, setDownloadingTicket] = useState(false);
  const [ticketError, setTicketError] = useState("");

  const {
    data: booking,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["booking", bookingId],
    queryFn: () =>
      apiGet<Booking>(`/api/v1/bookings/${bookingId}`),
    enabled: Boolean(bookingId),
    refetchInterval: 15000,
  });

  useEffect(() => {
    const interval = window.setInterval(() => {
      setNow(Date.now());
    }, 1000);

    return () => window.clearInterval(interval);
  }, []);

  const remaining = booking?.expires_at
    ? Math.max(0, new Date(booking.expires_at).getTime() - now)
    : 0;

  const isPending = booking?.status === "pending";
  const timeExpired = isPending && booking?.expires_at && remaining <= 0;

  useEffect(() => {
    if (timeExpired) {
      queryClient.invalidateQueries({
        queryKey: ["booking", bookingId],
      });
    }
  }, [timeExpired, bookingId, queryClient]);

  async function handleTicketDownload() {
    if (!booking || downloadingTicket) return;

    setDownloadingTicket(true);
    setTicketError("");

    try {
      await downloadBookingTicket(booking.id);
    } catch (error) {
      setTicketError(
        error instanceof Error
          ? error.message
          : "Unable to download your demo ticket."
      );
    } finally {
      setDownloadingTicket(false);
    }
  }

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50">
        <p className="text-slate-500">Loading your booking...</p>



</main>
    );
  }

  if (isError || !booking) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
        <section className="max-w-lg rounded-3xl bg-white p-10 text-center shadow-sm">
          <h1 className="text-2xl font-bold">Booking unavailable</h1>
          <p className="mt-3 text-slate-500">
            {error instanceof Error ? error.message : "Booking not found."}
          </p>
          <button
            onClick={() => navigate("/")}
            className="mt-6 rounded-xl bg-blue-600 px-6 py-3 text-white"
          >
            Back to Home
          </button>
        </section>
      </main>
    );
  }

  const isExpired = booking.status === "expired" || Boolean(timeExpired);
  const isCancelled = booking.status === "cancelled";
  const isConfirmed = booking.status === "confirmed";

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-12 text-slate-900">
      <div className="mx-auto max-w-2xl">
        <button
          onClick={() => navigate("/")}
          className="mb-8 inline-flex items-center gap-2 text-sm text-slate-600 hover:text-blue-600"
        >
          <ArrowLeft size={18} />
          Back to Home
        </button>

        <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm sm:p-10">
          <div className="text-center">
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-blue-50 text-blue-600">
              <CheckCircle2 size={40} />
            </div>

            <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
              AeroSky Demo Booking
            </p>

            <h1 className="mt-3 text-3xl font-bold">
              {isExpired
                ? "Reservation expired"
                : isCancelled
                ? "Reservation cancelled"
                : isConfirmed
                ? "Booking confirmed"
                : "Reservation created"}
            </h1>

            <p className="mt-4 text-slate-500">
              {isPending && !isExpired
                ? "Your seats are temporarily reserved."
                : isConfirmed
                ? "Your demo booking is confirmed."
                : "This reservation is no longer active."}
            </p>
          </div>

          <div className="mt-9 rounded-2xl bg-slate-50 p-7 text-center">
            <p className="text-xs uppercase tracking-widest text-slate-500">
              Booking reference
            </p>

            <p className="mt-2 break-all text-2xl font-bold text-blue-700">
              {booking.booking_reference}
            </p>

            <div className="mt-6 flex items-center justify-center gap-2">
              <Clock3 size={18} className="text-amber-600" />
              <span className="font-semibold capitalize">
                {isExpired ? "Expired" : booking.status}
              </span>
            </div>

            <p className="mt-6 text-sm text-slate-500">
              Total demo fare
            </p>

            <p className="mt-1 text-3xl font-bold">
              ₹{Number(booking.total_amount).toLocaleString("en-IN")}
            </p>
          </div>

          {isPending && !isExpired && booking.expires_at && (
            <div className="mt-7 rounded-2xl border border-blue-100 bg-blue-50 p-6 text-center">
              <div className="mb-2 flex items-center justify-center gap-2 text-blue-700">
                <CalendarClock size={20} />
                <span className="font-semibold">
                  Reservation expires in
                </span>
              </div>

              <p className="text-4xl font-extrabold tabular-nums text-blue-700">
                {formatRemaining(remaining)}
              </p>

              <p className="mt-3 text-xs text-blue-700">
                Payment must be completed before the reservation expires.
              </p>
            </div>
          )}

          {isPending && !isExpired && (
            <div className="mt-7 rounded-2xl border border-slate-200 bg-white p-6">
              <h2 className="mb-2 text-xl font-bold text-slate-900">
                Secure Payment
              </h2>

              <p className="mb-5 text-sm text-slate-600">
                Complete payment before your reservation expires.
              </p>

              <PaymentButton bookingId={booking.id} />
            </div>
          )}

          <div className="mt-7 flex items-start gap-3 rounded-2xl bg-slate-50 p-5 text-sm text-slate-600">
            <ShieldCheck size={20} className="shrink-0 text-blue-600" />
            <p>
              {isConfirmed
                ? "This is a demonstration flight booking. Payment was simulated using Razorpay Test Mode. No real money was charged, and no airline ticket has been issued."
                : "This is a demonstration flight booking. No real airline ticket has been issued. Payment has not been confirmed."}
            </p>
          </div>

          <div className="mt-7 flex justify-center gap-3 text-sm text-slate-500">
            <Plane size={18} />
            <span>
              Flight ID: {booking.flight_id} · {booking.passenger_count} passenger(s)
            </span>
          </div>

          {isConfirmed && (
            <div className="mt-8">
              <button
                type="button"
                onClick={handleTicketDownload}
                disabled={downloadingTicket}
                className="flex w-full items-center justify-center gap-2 rounded-2xl bg-emerald-600 px-6 py-4 font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {downloadingTicket
                  ? "Downloading PDF..."
                  : "Download E-Ticket (PDF)"}
              </button>

              {ticketError && (
                <p
                  role="alert"
                  className="mt-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
                >
                  {ticketError}
                </p>
              )}
            </div>
          )}

          <button
            onClick={() => navigate("/")}
            className="mt-9 w-full rounded-2xl bg-blue-600 px-6 py-4 font-semibold text-white transition hover:bg-blue-700"
          >
            Back to Home
          </button>
        </section>
      </div>
    </main>
  );
}
