import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowRight,
  CalendarDays,
  Plane,
  Ticket,
} from "lucide-react";
import { apiGet } from "../lib/api";

type Booking = {
  id: number;
  booking_reference: string;
  flight_id: number;
  flight: {
    flight_number: string;
    departure_time: string;
    arrival_time: string;
    origin: { code: string; city: string };
    destination: { code: string; city: string };
    airline: { name: string };
  };
  passenger_count: number;
  total_amount: string;
  currency: string;
  status: string;
  created_at: string;
  expires_at: string | null;
};

function statusStyle(status: string) {
  switch (status) {
    case "confirmed":
      return "bg-emerald-100 text-emerald-700";
    case "pending":
      return "bg-amber-100 text-amber-700";
    case "cancelled":
      return "bg-slate-100 text-slate-600";
    case "expired":
      return "bg-red-100 text-red-700";
    default:
      return "bg-slate-100 text-slate-600";
  }
}

export default function MyBookingsPage() {
  const {
    data: bookings,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["my-bookings"],
    queryFn: () => apiGet<Booking[]>("/api/v1/bookings/my"),
    staleTime: 0,
    refetchOnMount: "always",
  });

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-12 text-slate-900">
      <div className="mx-auto max-w-5xl">
        <div className="mb-10 flex flex-wrap items-center justify-between gap-4">
          <div>
            <Link
              to="/"
              className="text-sm font-semibold text-blue-700 hover:underline"
            >
              ← Back to Home
            </Link>
            <h1 className="mt-4 text-4xl font-extrabold tracking-tight">
              My Bookings
            </h1>
            <p className="mt-3 text-slate-500">
              View and manage your AeroSky demo reservations.
            </p>
          </div>

          <Link
            to="/"
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
          >
            <Plane size={18} />
            Book Another Flight
          </Link>
        </div>

        {isLoading && (
          <div className="rounded-3xl bg-white p-10 text-center text-slate-500">
            Loading your bookings...
          </div>
        )}

        {isError && (
          <div className="rounded-3xl border border-red-200 bg-white p-8">
            <p role="alert" className="text-red-700">
              {error instanceof Error
                ? error.message
                : "Unable to load bookings."}
            </p>
            <button
              type="button"
              onClick={() => void refetch()}
              className="mt-4 rounded-xl bg-blue-600 px-5 py-2.5 font-semibold text-white"
            >
              Try Again
            </button>
          </div>
        )}

        {!isLoading && !isError && bookings?.length === 0 && (
          <div className="rounded-3xl border border-slate-200 bg-white px-8 py-16 text-center shadow-sm">
            <Ticket className="mx-auto h-12 w-12 text-blue-600" />
            <h2 className="mt-5 text-2xl font-bold">
              No bookings yet
            </h2>
            <p className="mt-3 text-slate-500">
              Your flight reservations will appear here.
            </p>
            <Link
              to="/"
              className="mt-6 inline-flex rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white"
            >
              Explore Flights
            </Link>
          </div>
        )}

        {bookings && bookings.length > 0 && (
          <div className="space-y-5">
            {bookings.map((booking) => (
              <article
                key={booking.id}
                className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8"
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">
                      Booking Reference
                    </p>
                    <h2 className="mt-2 break-all text-xl font-bold text-slate-900">
                      {booking.booking_reference}
                    </h2>
                  </div>

                  <span
                    className={`rounded-full px-4 py-2 text-xs font-bold capitalize ${statusStyle(
                      booking.status
                    )}`}
                  >
                    {booking.status}
                  </span>
                </div>

                <div className="mt-6 rounded-2xl bg-blue-50 p-5">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold text-slate-500">FROM</p>
                      <p className="text-3xl font-extrabold text-blue-900">
                        {booking.flight.origin.code}
                      </p>
                      <p className="text-sm text-slate-600">
                        {booking.flight.origin.city}
                      </p>
                    </div>

                    <div className="flex flex-col items-center gap-2 text-center">
                      <Plane className="text-blue-600" size={25} />
                      <p className="text-xs font-semibold text-slate-600">
                        {booking.flight.airline.name}
                      </p>
                      <p className="text-xs text-slate-500">
                        {booking.flight.flight_number}
                      </p>
                    </div>

                    <div className="text-right">
                      <p className="text-xs font-semibold text-slate-500">TO</p>
                      <p className="text-3xl font-extrabold text-blue-900">
                        {booking.flight.destination.code}
                      </p>
                      <p className="text-sm text-slate-600">
                        {booking.flight.destination.city}
                      </p>
                    </div>
                  </div>

                  <p className="mt-4 border-t border-blue-100 pt-3 text-sm text-slate-700">
                    <span className="font-semibold">Departure:</span>{" "}
                    {new Date(booking.flight.departure_time).toLocaleString(
                      "en-IN",
                      {
                        timeZone: "Asia/Kolkata",
                        day: "2-digit",
                        month: "short",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                        hour12: false,
                      }
                    )} IST
                  </p>
                </div>

                <div className="mt-6 grid gap-5 border-y border-slate-100 py-6 sm:grid-cols-4">
                  <div>
                    <p className="text-xs text-slate-500">Flight Number</p>
                    <p className="mt-1 font-bold">
                      {booking.flight.flight_number}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-slate-500">Passengers</p>
                    <p className="mt-1 font-bold">
                      {booking.passenger_count}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-slate-500">Demo Fare</p>
                    <p className="mt-1 font-bold">
                      {new Intl.NumberFormat("en-IN", {
                        style: "currency",
                        currency: booking.currency,
                      }).format(Number(booking.total_amount))}
                    </p>
                  </div>

                  <div>
                    <p className="flex items-center gap-1 text-xs text-slate-500">
                      <CalendarDays size={14} />
                      Booked On
                    </p>
                    <p className="mt-1 font-bold">
                      {new Date(booking.created_at).toLocaleDateString(
                        "en-IN",
                        {
                          day: "2-digit",
                          month: "short",
                          year: "numeric",
                        }
                      )}
                    </p>
                  </div>
                </div>

                <div className="mt-6 flex justify-end">
                  <Link
                    to={`/booking/${booking.id}`}
                    className="inline-flex items-center gap-2 font-semibold text-blue-700 hover:underline"
                  >
                    View Booking
                    <ArrowRight size={18} />
                  </Link>
                </div>
              </article>
            ))}
          </div>
        )}

        <p className="mt-10 text-center text-xs text-slate-400">
          AeroSky is a demonstration application. No real airline
          reservations or travel tickets are issued.
        </p>
      </div>
    </main>
  );
}
