import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRightLeft,
  CalendarDays,
  Plane,
  Search,
  SlidersHorizontal,
} from "lucide-react";

import FlightCard from "../components/FlightCard";
import { apiGet } from "../lib/api";
import type { Flight } from "../types/flight";

type SortOption = "price" | "departure" | "duration";

export default function FlightResultsPage() {
  const [params] = useSearchParams();
  const [sortBy, setSortBy] = useState<SortOption>("price");

  const origin = (params.get("origin") ?? "").toUpperCase();
  const destination = (params.get("destination") ?? "").toUpperCase();
  const departureDate = params.get("departure_date") ?? "";
  const passengers = Number(params.get("passengers") ?? "1");
  const cabinClass = params.get("cabin_class") ?? "economy";
  const tripType = params.get("trip_type") ?? "one-way";
  const returnDate = params.get("return_date") ?? "";


  const validSearch =
    /^[A-Z]{3}$/.test(origin) &&
    /^[A-Z]{3}$/.test(destination) &&
    origin !== destination &&
    /^\d{4}-\d{2}-\d{2}$/.test(departureDate) &&
    Number.isInteger(passengers) &&
    passengers >= 1 &&
    passengers <= 9;

  const queryString = useMemo(() => {
    const query = new URLSearchParams({
      origin,
      destination,
      departure_date: departureDate,
      passengers: String(passengers),
      cabin_class: cabinClass,
      limit: "100",
    });

    return query.toString();
  }, [origin, destination, departureDate, passengers, cabinClass]);

  const {
    data: flights = [],
    isPending,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["flights", queryString],
    queryFn: ({ signal }) =>
      apiGet<Flight[]>(`/api/v1/flights/search?${queryString}`, signal),
    enabled: validSearch,
  });

  const sortedFlights = useMemo(() => {
    const result = [...flights];

    if (sortBy === "price") {
      result.sort((a, b) => Number(a.price) - Number(b.price));
    } else if (sortBy === "departure") {
      result.sort(
        (a, b) =>
          new Date(a.departure_time).getTime() -
          new Date(b.departure_time).getTime()
      );
    } else {
      result.sort((a, b) => {
        const durationA =
          new Date(a.arrival_time).getTime() -
          new Date(a.departure_time).getTime();

        const durationB =
          new Date(b.arrival_time).getTime() -
          new Date(b.departure_time).getTime();

        return durationA - durationB;
      });
    }

    return result;
  }, [flights, sortBy]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
          <Link to="/" className="flex items-center gap-2 text-xl font-extrabold tracking-tight text-slate-900">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white">
              <Plane size={21} />
            </span>
            Aero<span className="text-blue-600">Sky</span>
          </Link>

          <Link
            to="/"
            className="flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            <ArrowLeft size={16} />
            Back to Search
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-10 sm:px-8">
        <div className="mb-8">
          <span className="mb-3 inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700">
            <Plane size={14} />
            AEROSKY FLIGHT DISCOVERY
          </span>

          <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl">
            Find your perfect flight
          </h1>

          <p className="mt-2 text-slate-500">
            Explore available demo flights and compare fares.
          </p>
        </div>

        <section className="mb-8 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
          <div className="flex flex-wrap items-center gap-6">
            <div className="flex items-center gap-3">
              <div>
                <p className="text-xs text-slate-500">From</p>
                <p className="text-xl font-extrabold">{origin || "—"}</p>
              </div>

              <ArrowRightLeft size={19} className="text-blue-600" />

              <div>
                <p className="text-xs text-slate-500">To</p>
                <p className="text-xl font-extrabold">{destination || "—"}</p>
              </div>
            </div>

            <div className="hidden h-10 w-px bg-slate-200 sm:block" />

            <div className="flex items-center gap-2">
              <CalendarDays size={19} className="text-blue-600" />
              <div>
                <p className="text-xs text-slate-500">Departure</p>
                <p className="font-bold">{departureDate || "Not selected"}</p>
              </div>
            </div>

            <div className="hidden h-10 w-px bg-slate-200 sm:block" />

            <div>
              <p className="text-xs text-slate-500">Travellers</p>
              <p className="font-bold">
                {passengers} · {cabinClass.replaceAll("_", " ")}
              </p>
            </div>

            <Link
              to="/"
              className="ml-auto flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700"
            >
              <Search size={17} />
              Modify Search
            </Link>
          </div>
        </section>

        {tripType === "round-trip" && (
          <div className="mb-6 rounded-2xl border border-blue-200 bg-blue-50 p-5">
            <p className="font-bold text-blue-900">
              Round-trip search
            </p>
            <p className="mt-1 text-sm text-blue-800">
              Outbound flights are shown below. Return date:{" "}
              <strong>{returnDate || "Not selected"}</strong>.
              Return-flight search and combined fares will be
              available in a later step.
            </p>
          </div>
        )}

        <div className="mb-5 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-extrabold">
              Available Flights
            </h2>
            <p className="text-sm text-slate-500">
              {validSearch && !isPending && !isError
                ? `${sortedFlights.length} flights found`
                : "Search results"}
            </p>
          </div>

          <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3">
            <SlidersHorizontal size={17} className="text-slate-500" />
            <label htmlFor="flight-sort" className="text-sm font-medium text-slate-600">
              Sort by
            </label>
            <select
              id="flight-sort"
              value={sortBy}
              onChange={(event) => setSortBy(event.target.value as SortOption)}
              className="bg-transparent text-sm font-bold text-slate-900 outline-none"
            >
              <option value="price">Lowest Price</option>
              <option value="departure">Earliest Departure</option>
              <option value="duration">Shortest Duration</option>
            </select>
          </div>
        </div>

        {!validSearch ? (
          <div className="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center">
            <h3 className="text-xl font-bold">Search details are missing</h3>
            <p className="mt-2 text-slate-500">
              Please choose your airports and departure date.
            </p>
            <Link to="/" className="mt-5 inline-block font-bold text-blue-600">
              Return to flight search
            </Link>
          </div>
        ) : isPending ? (
          <div className="space-y-4">
            {[1, 2, 3].map((item) => (
              <div
                key={item}
                className="h-52 animate-pulse rounded-3xl border border-slate-200 bg-white"
              />
            ))}
          </div>
        ) : isError ? (
          <div className="rounded-3xl border border-red-100 bg-white px-6 py-14 text-center">
            <h3 className="text-xl font-bold text-slate-900">
              Unable to load flights
            </h3>
            <p className="mt-2 text-sm text-red-600">
              {error instanceof Error ? error.message : "Something went wrong."}
            </p>
            <button
              onClick={() => void refetch()}
              className="mt-5 rounded-xl bg-blue-600 px-5 py-3 font-bold text-white"
            >
              Try Again
            </button>
          </div>
        ) : sortedFlights.length === 0 ? (
          <div className="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center">
            <Plane size={36} className="mx-auto mb-4 text-blue-500" />
            <h3 className="text-xl font-bold">No flights found</h3>
            <p className="mt-2 text-slate-500">
              Try another route or departure date.
            </p>
            <Link to="/" className="mt-5 inline-block font-bold text-blue-600">
              Modify your search
            </Link>
          </div>
        ) : (
          <div className="space-y-5">
            {sortedFlights.map((flight) => (
              <FlightCard key={flight.id} flight={flight} />
            ))}
          </div>
        )}

        <p className="mt-10 text-center text-xs text-slate-400">
          AeroSky currently uses simulated flight inventory for demonstration purposes.
          No real airline tickets are issued.
        </p>
      </main>
    </div>
  );
}
