
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeftRight,
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  MapPin,
  Minus,
  Plane,
  Plus,
  Search,
  Users,
  X,
} from "lucide-react";

type TripType = "one-way" | "round-trip";
type CabinClass = "Economy" | "Premium Economy" | "Business" | "First";

type Airport = {
  code: string;
  city: string;
  name: string;
  country: string;
};

const API_BASE = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");


const today = () => {
  const now = new Date();
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
};

const fieldClass =
  "h-[72px] w-full min-w-0 rounded-xl border border-slate-200 bg-[#f8fafc] px-4 pt-5 text-sm font-semibold text-slate-900 outline-none transition focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10";

function AirportField({
  label,
  value,
  onChange,
  icon,
  airports,
  loading,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  icon: ReactNode;
  airports: Airport[];
  loading: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  const selected = airports.find((airport) => airport.code === value);
  const filtered = airports.filter((airport) =>
    `${airport.city} ${airport.code} ${airport.name} ${airport.country}`
      .toLowerCase()
      .includes(query.trim().toLowerCase())
  );

  return (
    <div className="relative min-w-0">
      <span className="pointer-events-none absolute left-11 top-3 z-10 text-[11px] font-semibold text-slate-600">
        {label}
      </span>

      <span className="pointer-events-none absolute left-4 top-9 text-slate-500">
        {icon}
      </span>

      <button
        type="button"
        aria-label={label}
        aria-expanded={open}
        onClick={() => {
          setOpen((previous) => !previous);
          setQuery("");
        }}
        className={`${fieldClass} flex items-center justify-between gap-2 pl-11 pr-3 text-left`}
      >
        <span className="truncate">
          {selected
            ? `${selected.city} (${selected.code})`
            : loading
              ? "Loading airports..."
              : "Select airport"}
        </span>
        <ChevronDown size={14} className="shrink-0 text-slate-500" />
      </button>

      {open && (
        <div className="absolute left-0 top-[78px] z-50 w-full min-w-[240px] rounded-xl border border-slate-200 bg-white p-2 shadow-2xl">
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search city, country, airport..."
            aria-label={`Search ${label.toLowerCase()} airports`}
            autoFocus
            className="mb-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500"
          />

          <div className="max-h-60 overflow-y-auto">
            {filtered.map((airport) => (
              <button
                key={airport.code}
                type="button"
                onClick={() => {
                  onChange(airport.code);
                  setOpen(false);
                  setQuery("");
                }}
                className={`block w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-blue-50 ${
                  airport.code === value
                    ? "bg-blue-50 font-semibold text-blue-700"
                    : "text-slate-800"
                }`}
              >
                <span className="block">
                  {airport.city} ({airport.code})
                </span>
                <span className="block truncate text-xs text-slate-500">
                  {airport.name} ? {airport.country}
                </span>
              </button>
            ))}

            {filtered.length === 0 && (
              <p className="px-3 py-3 text-sm text-slate-500">
                {loading ? "Loading airports..." : "No airports found."}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function PassengerCounter({
  label,
  subtitle,
  count,
  onDecrease,
  onIncrease,
  canDecrease,
  canIncrease,
}: {
  label: string;
  subtitle: string;
  count: number;
  onDecrease: () => void;
  onIncrease: () => void;
  canDecrease: boolean;
  canIncrease: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4 py-3">
      <div>
        <p className="text-sm font-semibold text-slate-900">
          {label}
        </p>
        <p className="text-xs text-slate-500">
          {subtitle}
        </p>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onDecrease}
          disabled={!canDecrease}
          aria-label={`Remove ${label.toLowerCase()}`}
          className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 disabled:cursor-not-allowed disabled:opacity-30"
        >
          <Minus size={14} />
        </button>

        <span className="w-4 text-center text-sm font-bold text-slate-900">
          {count}
        </span>

        <button
          type="button"
          onClick={onIncrease}
          disabled={!canIncrease}
          aria-label={`Add ${label.toLowerCase()}`}
          className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 disabled:cursor-not-allowed disabled:opacity-30"
        >
          <Plus size={14} />
        </button>
      </div>
    </div>
  );
}

export default function FlightSearch() {
  const navigate = useNavigate();
  const [airports, setAirports] = useState<Airport[]>([]);
  const [airportLoading, setAirportLoading] = useState(true);
  const [airportError, setAirportError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadAirports() {
      try {
        const response = await fetch(
          `${API_BASE}/api/v1/airports`,
          { signal: controller.signal }
        );

        if (!response.ok) {
          throw new Error("Unable to load airports.");
        }

        const data: Airport[] = await response.json();
        setAirports(data);
        setAirportError("");
      } catch (error) {
        if (!controller.signal.aborted) {
          setAirportError(
            "Could not load airports. Check that the backend is running."
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setAirportLoading(false);
        }
      }
    }

    void loadAirports();

    return () => controller.abort();
  }, []);

  const [tripType, setTripType] = useState<TripType>("one-way");
  const [from, setFrom] = useState("HYD");
  const [to, setTo] = useState("DEL");
  const [departure, setDeparture] = useState(today());
  const [returnDate, setReturnDate] = useState(today());

  const [adults, setAdults] = useState(1);
  const [children, setChildren] = useState(0);
  const [cabin, setCabin] = useState<CabinClass>("Economy");

  const [passengerOpen, setPassengerOpen] = useState(false);
  const [error, setError] = useState("");


  const passengerTotal = adults + children;

  const swapAirports = () => {
    setFrom(to);
    setTo(from);
  };

  const handleSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError("");
    if (airportLoading || airportError || airports.length === 0) {
      setError("Airports are unavailable. Please try again.");
      return;
    }

    if (
      !airports.some((airport) => airport.code === from) ||
      !airports.some((airport) => airport.code === to)
    ) {
      setError("Please select valid departure and destination airports.");
      return;
    }

    if (from === to) {
      setError("Departure and destination airports must be different.");
      return;
    }

    if (!departure || departure < today()) {
      setError("Please select a valid departure date.");
      return;
    }

    if (
      tripType === "round-trip" &&
      (!returnDate || returnDate < departure)
    ) {
      setError("Return date must be on or after the departure date.");
      return;
    }

    if (passengerTotal < 1 || passengerTotal > 9) {
      setError("Please select between 1 and 9 passengers.");
      return;
    }

    setPassengerOpen(false);

    const cabinMap: Record<CabinClass, string> = {
      Economy: "economy",
      "Premium Economy": "premium_economy",
      Business: "business",
      First: "first",
    };

    const params = new URLSearchParams({
      origin: from,
      destination: to,
      departure_date: departure,
      passengers: String(passengerTotal),
      adults: String(adults),
      children: String(children),
      cabin_class: cabinMap[cabin],
      trip_type: tripType,
    });

    if (tripType === "round-trip") {
      params.set("return_date", returnDate);
    }

    navigate(`/flights?${params.toString()}`);
  };

  return (
    <section
      id="flights"
      className="relative z-20 scroll-mt-6 text-slate-900"
    >
      {/* MAIN BOOKING CARD */}
      <div className="rounded-[24px] border border-slate-200 bg-white p-4 shadow-[0_20px_55px_rgba(9,36,87,0.18)] sm:p-5 lg:p-6">

        {/* CARD HEADER */}
        <div className="mb-5 flex flex-wrap items-center justify-between gap-4">

          <div className="flex items-center gap-3">
            <span className="flex items-center gap-2 rounded-full bg-blue-50 px-4 py-2.5 text-sm font-bold text-blue-700">
              <Plane size={17} />
              Flights
            </span>

            <span className="hidden text-xs font-medium text-slate-500 sm:inline">
              Find your next adventure
            </span>
          </div>

          {/* TRIP TYPE */}
          <div className="flex rounded-full bg-slate-100 p-1">
            {(["one-way", "round-trip"] as const).map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => {
                  setTripType(type);
                  setError("");
                }}
                className={`rounded-full px-4 py-2 text-xs font-semibold transition sm:text-sm ${
                  tripType === type
                    ? "bg-blue-700 text-white shadow-sm"
                    : "text-slate-600 hover:text-blue-700"
                }`}
              >
                {type === "one-way" ? "One way" : "Round trip"}
              </button>
            ))}
          </div>
        </div>

        {/* SEARCH FORM */}
        <form onSubmit={handleSearch} noValidate>
          <div
            className={`grid grid-cols-1 gap-3 md:grid-cols-2 ${
              tripType === "round-trip"
                ? "xl:grid-cols-12"
                : "xl:grid-cols-12"
            }`}
          >
            {/* AIRPORTS */}
            <div className="relative md:col-span-2 xl:col-span-5">
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <AirportField
                  label="From"
                  airports={airports}
                  loading={airportLoading}
                  value={from}
                  onChange={(value) => {
                    setFrom(value);
                  }}
                  icon={<MapPin size={17} />}
                />

                <AirportField
                  label="To"
                  airports={airports}
                  loading={airportLoading}
                  value={to}
                  onChange={(value) => {
                    setTo(value);
                  }}
                  icon={<MapPin size={17} />}
                />
              </div>

              <button
                type="button"
                onClick={swapAirports}
                aria-label="Swap departure and destination"
                className="absolute left-1/2 top-1/2 z-10 flex h-9 w-9 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-blue-100 bg-white text-blue-700 shadow-md transition hover:bg-blue-50"
              >
                <ArrowLeftRight size={16} />
              </button>
            </div>

            {/* DEPARTURE DATE */}
            <label className="relative block min-w-0 xl:col-span-2">
              <span className="absolute left-4 top-3 z-10 text-[11px] font-semibold text-slate-600">
                Departure
              </span>

              <CalendarDays
                size={16}
                className="pointer-events-none absolute left-4 top-9 text-slate-500"
              />

              <input
                type="date"
                value={departure}
                min={today()}
                onChange={(event) => {
                  const value = event.target.value;
                  setDeparture(value);
                  if (value && value > returnDate) {
                    setReturnDate(value);
                  }
                }}
                required
                aria-label="Departure date"
                className={`${fieldClass} pl-10 pr-2`}
              />
            </label>

            {/* RETURN DATE */}
            {tripType === "round-trip" && (
              <label className="relative block min-w-0 xl:col-span-2">
                <span className="absolute left-4 top-3 z-10 text-[11px] font-semibold text-slate-600">
                  Return
                </span>

                <CalendarDays
                  size={16}
                  className="pointer-events-none absolute left-4 top-9 text-slate-500"
                />

                <input
                  type="date"
                  value={returnDate}
                  min={departure || today()}
                  onChange={(event) => {
                    setReturnDate(event.target.value);
                  }}
                  required
                  aria-label="Return date"
                  className={`${fieldClass} pl-10 pr-2`}
                />
              </label>
            )}

            {/* PASSENGERS */}
            <div className="relative min-w-0 xl:col-span-3">
              <button
                type="button"
                onClick={() => setPassengerOpen((open) => !open)}
                aria-expanded={passengerOpen}
                aria-label="Passengers and cabin class"
                className={`${fieldClass} relative flex items-center gap-3 text-left`}
              >
                <Users
                  size={17}
                  className="shrink-0 text-slate-500"
                />

                <span className="min-w-0 flex-1">
                  <span className="block text-[11px] font-semibold text-slate-600">
                    Passengers & class
                  </span>

                  <span className="block truncate text-sm font-semibold text-slate-900">
                    {passengerTotal} traveller
                    {passengerTotal !== 1 ? "s" : ""}, {cabin}
                  </span>
                </span>

                <ChevronDown
                  size={15}
                  className="shrink-0 text-slate-500"
                />
              </button>

              {/* PASSENGER POPUP */}
              {passengerOpen && (
                <div className="absolute right-0 top-[80px] z-50 w-full min-w-[270px] rounded-2xl border border-slate-200 bg-white p-5 text-slate-900 shadow-2xl sm:w-[310px]">

                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-slate-900">
                      Travellers
                    </h3>

                    <button
                      type="button"
                      aria-label="Close passenger selector"
                      onClick={() => setPassengerOpen(false)}
                      className="text-slate-500 hover:text-slate-900"
                    >
                      <X size={18} />
                    </button>
                  </div>

                  <PassengerCounter
                    label="Adults"
                    subtitle="12 years and above"
                    count={adults}
                    onDecrease={() =>
                      setAdults((n) => Math.max(1, n - 1))
                    }
                    onIncrease={() =>
                      setAdults((n) =>
                        Math.min(9 - children, n + 1)
                      )
                    }
                    canDecrease={adults > 1}
                    canIncrease={passengerTotal < 9}
                  />

                  <PassengerCounter
                    label="Children"
                    subtitle="2 to 11 years"
                    count={children}
                    onDecrease={() =>
                      setChildren((n) => Math.max(0, n - 1))
                    }
                    onIncrease={() =>
                      setChildren((n) =>
                        Math.min(9 - adults, n + 1)
                      )
                    }
                    canDecrease={children > 0}
                    canIncrease={passengerTotal < 9}
                  />

                  <label className="mt-3 block text-xs font-semibold text-slate-600">
                    Cabin class

                    <select
                      value={cabin}
                      onChange={(event) => {
                        setCabin(
                          event.target.value as CabinClass
                        );
                      }}
                      className="mt-2 w-full rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-900"
                    >
                      <option>Economy</option>
                      <option>Premium Economy</option>
                      <option>Business</option>
                      <option>First</option>
                    </select>
                  </label>

                  <button
                    type="button"
                    onClick={() => setPassengerOpen(false)}
                    className="mt-4 w-full rounded-xl bg-blue-700 py-3 text-sm font-bold text-white hover:bg-blue-800"
                  >
                    Done
                  </button>
                </div>
              )}
            </div>

            {/* SEARCH BUTTON */}
            <button
              type="submit"
              className={`flex h-[72px] min-w-0 items-center justify-center gap-2 whitespace-nowrap rounded-xl bg-blue-700 px-3 text-sm font-bold text-white shadow-lg shadow-blue-700/20 transition hover:bg-blue-800 ${
                tripType === "round-trip"
                  ? "md:col-span-2 xl:col-span-12"
                  : "md:col-span-2 xl:col-span-2"
              }`}
            >
              <Search size={18} className="shrink-0" />
              <span>Search Flights</span>
              <ArrowRight size={16} className="shrink-0" />
            </button>
          </div>

          {airportError && (
            <p role="alert" className="mt-4 text-sm text-red-700">
              {airportError}
            </p>
          )}

          {/* ERROR MESSAGE */}
          {error && (
            <p
              role="alert"
              className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
            >
              {error}
            </p>
          )}
        </form>

        {/* CARD FOOTER */}
        <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs font-medium text-slate-600">
          <span className="flex items-center gap-1.5">
            <CheckCircle2 size={14} className="text-blue-600" />
            Transparent fare breakdown
          </span>

          <span className="flex items-center gap-1.5">
            <CheckCircle2 size={14} className="text-blue-600" />
            Seat selection
          </span>

          <span className="flex items-center gap-1.5">
            <CheckCircle2 size={14} className="text-blue-600" />
            Secure test checkout
          </span>
        </div>
      </div>


    </section>
  );
}
