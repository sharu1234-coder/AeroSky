import AircraftSeatMap from "../components/AircraftSeatMap";
import { useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, Plane, ShieldCheck } from "lucide-react";
import { apiGet } from "../lib/api";
import type { Flight } from "../types/flight";

type PassengerType = "adult" | "child";

type PassengerForm = {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  passenger_type: PassengerType;
};

export default function PassengerDetailsPage() {
  const { flightId } = useParams();
  const navigate = useNavigate();

  const params = new URLSearchParams(window.location.search);

  const passengerCount = Math.min(
    9,
    Math.max(1, Number(params.get("passengers")) || 1)
  );

  const adultCount = Math.min(
    passengerCount,
    Math.max(0, Number(params.get("adults")) || passengerCount)
  );

  const [passengers, setPassengers] = useState<PassengerForm[]>(
    Array.from({ length: passengerCount }, (_, index) => ({
      first_name: "",
      last_name: "",
      date_of_birth: "",
      passenger_type: index < adultCount ? "adult" : "child",
    }))
  );

  const [selectedSeats, setSelectedSeats] = useState<string[]>([]);

  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState("");

  const {
    data: flight,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["checkout-flight", flightId],
    queryFn: async () => {
      const response = await apiGet<Flight[]>(
        `/api/v1/flights/search?origin=${encodeURIComponent(
          params.get("origin") ?? ""
        )}&destination=${encodeURIComponent(
          params.get("destination") ?? ""
        )}&departure_date=${encodeURIComponent(
          params.get("departure_date") ?? ""
        )}&passengers=${passengerCount}&limit=100`
      );

      return response.find((item) => item.id === Number(flightId));
    },
    enabled: Boolean(flightId),
  });

  const total = useMemo(() => {
    return Number(flight?.price ?? 0) * passengerCount;
  }, [flight, passengerCount]);

  function updatePassenger(
    index: number,
    field: keyof PassengerForm,
    value: string
  ) {
    setPassengers((current) =>
      current.map((passenger, i) =>
        i === index ? { ...passenger, [field]: value } : passenger
      )
    );
  }

  async function submitBooking(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (!flight) {
      setError("Please select a valid flight.");
      return;
    }

    if (passengers.some((p) =>
      !p.first_name.trim() || !p.last_name.trim() || !p.date_of_birth
    )) {
      setError("Please complete all passenger details.");
      return;
    }

    if (selectedSeats.length !== passengerCount) {
      setError("Please select one seat for every passenger.");
      return;
    }

    navigate("/checkout/food", {
      state: {
        checkout: {
          flight_id: flight.id,
          contact_email: email,
          contact_phone: phone,
          passengers: passengers.map((passenger, index) => ({
            ...passenger,
            seat_number: selectedSeats[index],
          })),
        },
      },
    });
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-slate-50 p-10 text-center">
        Loading flight details...
      </main>
    );
  }

  if (isError || !flight) {
    return (
      <main className="min-h-screen bg-slate-50 p-10 text-center">
        <h1 className="text-2xl font-semibold">Flight unavailable</h1>
        <p className="mt-3 text-slate-500">
          Return to flight results and select another flight.
        </p>
        <button
          onClick={() => navigate(-1)}
          className="mt-6 rounded-xl bg-blue-600 px-6 py-3 text-white"
        >
          Go Back
        </button>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 text-slate-900">
      <div className="mx-auto max-w-6xl">
        <button
          onClick={() => navigate(-1)}
          className="mb-8 flex items-center gap-2 text-sm text-slate-600"
        >
          <ArrowLeft size={18} /> Back to flights
        </button>

        <div className="mb-9">
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
            AeroSky Booking
          </p>
          <h1 className="mt-2 text-4xl font-bold tracking-tight">
            Passenger details
          </h1>
          <p className="mt-3 text-slate-500">
            Complete your information to reserve your demo flight.
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-[1fr_340px]">
          <form onSubmit={submitBooking} className="space-y-6">
            {passengers.map((passenger, index) => (
              <section
                key={index}
                className="rounded-3xl border border-slate-200 bg-white p-7 shadow-sm"
              >
                <div className="mb-6 flex items-center justify-between">
                  <h2 className="text-xl font-semibold">
                    Passenger {index + 1}
                  </h2>
                  <span className="rounded-full bg-blue-50 px-4 py-2 text-xs font-semibold capitalize text-blue-700">
                    {passenger.passenger_type}
                  </span>
                </div>

                <div className="grid gap-5 sm:grid-cols-2">
                  <label className="text-sm font-medium">
                    First name
                    <input
                      required
                      maxLength={100}
                      value={passenger.first_name}
                      onChange={(e) =>
                        updatePassenger(index, "first_name", e.target.value)
                      }
                      className="mt-2 w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-blue-500"
                      placeholder="First name"
                    />
                  </label>

                  <label className="text-sm font-medium">
                    Last name
                    <input
                      required
                      maxLength={100}
                      value={passenger.last_name}
                      onChange={(e) =>
                        updatePassenger(index, "last_name", e.target.value)
                      }
                      className="mt-2 w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-blue-500"
                      placeholder="Last name"
                    />
                  </label>

                  <label className="text-sm font-medium sm:col-span-2">
                    Date of birth
                    <input
                      required
                      type="date"
                      max={new Date().toISOString().slice(0, 10)}
                      value={passenger.date_of_birth}
                      onChange={(e) =>
                        updatePassenger(index, "date_of_birth", e.target.value)
                      }
                      className="mt-2 w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-blue-500"
                    />
                  </label>
                </div>
              </section>
            ))}

            <section className="rounded-3xl border border-slate-200 bg-white p-7 shadow-sm">
              <h2 className="mb-6 text-xl font-semibold">
                Contact information
              </h2>

              <div className="grid gap-5 sm:grid-cols-2">
                <label className="text-sm font-medium">
                  Email address
                  <input
                    required
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-blue-500"
                    placeholder="you@example.com"
                  />
                </label>

                <label className="text-sm font-medium">
                  Phone number
                  <input
                    required
                    type="tel"
                    pattern="\+?[0-9]{10,15}"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-blue-500"
                    placeholder="9876543210"
                  />
                </label>
              </div>
            </section>

            <AircraftSeatMap
              flightId={flight.id}
              passengerCount={passengerCount}
              selectedSeats={selectedSeats}
              onChange={setSelectedSeats}
            />

            {error && (
              <p
                role="alert"
                className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
              >
                {error}
              </p>
            )}

            <button
              disabled={false}
              type="submit"
              className="flex w-full items-center justify-center gap-3 rounded-2xl bg-blue-600 px-6 py-4 font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
            >
              "Continue to Food Selection"
              <ArrowRight size={19} />
            </button>
          </form>

          <aside className="h-fit rounded-3xl border border-slate-200 bg-white p-7 shadow-sm lg:sticky lg:top-8">
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-xl bg-blue-50 p-3 text-blue-600">
                <Plane size={22} />
              </div>
              <div>
                <p className="text-xs uppercase text-slate-400">
                  Your selected flight
                </p>
                <h3 className="font-semibold">
                  {flight.airline.name} · {flight.flight_number}
                </h3>
              </div>
            </div>

            <div className="mb-6 flex justify-between text-2xl font-bold">
              <span>{flight.origin.code}</span>
              <ArrowRight className="text-blue-500" />
              <span>{flight.destination.code}</span>
            </div>

            <div className="space-y-3 border-t border-slate-100 pt-5 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Passengers</span>
                <span>{passengerCount}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Fare per passenger</span>
                <span>₹{Number(flight.price).toLocaleString("en-IN")}</span>
              </div>
              <div className="flex justify-between border-t border-slate-100 pt-4 text-lg font-bold">
                <span>Estimated total</span>
                <span>₹{total.toLocaleString("en-IN")}</span>
              </div>
            </div>

            <div className="mt-7 flex gap-3 rounded-2xl bg-blue-50 p-4 text-xs leading-relaxed text-blue-800">
              <ShieldCheck className="shrink-0" size={20} />
              This is a demonstration booking. No real airline ticket will be issued.
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}
