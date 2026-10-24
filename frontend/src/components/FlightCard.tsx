import { useNavigate, useLocation } from "react-router-dom";
import { ArrowRight, Clock3, Plane, Users } from "lucide-react";
import type { Flight } from "../types/flight";

interface FlightCardProps {
  flight: Flight;
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "Asia/Kolkata",
  }).format(new Date(value));
}

function formatDuration(departure: string, arrival: string) {
  const minutes = Math.max(
    0,
    Math.round(
      (new Date(arrival).getTime() - new Date(departure).getTime()) /
        60000
    )
  );

  const hours = Math.floor(minutes / 60);
  const remaining = minutes % 60;

  return `${hours}h ${remaining}m`;
}

export default function FlightCard({ flight }: FlightCardProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const price = Number(flight.price);

  function selectFlight() {
    const searchParams = new URLSearchParams(location.search);

    // Ensure the checkout page always receives the selected flight route.
    searchParams.set("origin", flight.origin.code);
    searchParams.set("destination", flight.destination.code);

    // Use the flight's actual India-local departure date.
    const departureDate = new Intl.DateTimeFormat("en-CA", {
      timeZone: "Asia/Kolkata",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).format(new Date(flight.departure_time));

    searchParams.set("departure_date", departureDate);

    if (!searchParams.has("passengers")) {
      searchParams.set("passengers", "1");
    }

    navigate(`/checkout/${flight.id}?${searchParams.toString()}`);
  }

  return (
    <article className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
      <div className="p-5 sm:p-7">
        <div className="mb-7 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
              <Plane size={23} />
            </div>

            <div>
              <h3 className="font-bold text-slate-900">
                {flight.airline.name}
              </h3>
              <p className="text-sm text-slate-500">
                {flight.flight_number} · {flight.cabin_class.replaceAll("_", " ")}
              </p>
            </div>
          </div>

          <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
            Available
          </span>
        </div>

        <div className="grid gap-6 md:grid-cols-[1fr_1.2fr_1fr_auto] md:items-center">
          <div>
            <p className="text-3xl font-extrabold text-slate-900">
              {formatTime(flight.departure_time)}
            </p>
            <p className="mt-1 font-bold text-slate-800">
              {flight.origin.code}
            </p>
            <p className="text-sm text-slate-500">
              {flight.origin.city}
            </p>
          </div>

          <div className="text-center">
            <div className="mb-2 flex items-center justify-center gap-2 text-sm text-slate-500">
              <Clock3 size={15} />
              {formatDuration(
                flight.departure_time,
                flight.arrival_time
              )}
            </div>

            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full border-2 border-blue-500" />
              <div className="h-px flex-1 bg-slate-300" />
              <Plane size={18} className="text-blue-600" />
              <div className="h-px flex-1 bg-slate-300" />
              <div className="h-2 w-2 rounded-full border-2 border-blue-500" />
            </div>

            <p className="mt-2 text-xs font-medium text-slate-500">
              Demo flight
            </p>
          </div>

          <div className="md:text-right">
            <p className="text-3xl font-extrabold text-slate-900">
              {formatTime(flight.arrival_time)}
            </p>
            <p className="mt-1 font-bold text-slate-800">
              {flight.destination.code}
            </p>
            <p className="text-sm text-slate-500">
              {flight.destination.city}
            </p>
          </div>

          <div className="md:border-l md:border-slate-200 md:pl-7">
            <p className="text-xs text-slate-500">From</p>

            <p className="mt-1 whitespace-nowrap text-2xl font-extrabold text-blue-700">
              {new Intl.NumberFormat("en-IN", {
                style: "currency",
                currency: "INR",
                maximumFractionDigits: 0,
              }).format(price)}
            </p>

            <p className="mt-1 flex items-center gap-1 text-xs text-slate-500">
              <Users size={13} />
              {flight.available_seats} seats left
            </p>

            <button
              type="button"
              onClick={selectFlight}
              disabled={flight.available_seats < 1}
              className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
            >
              Select Flight <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}
