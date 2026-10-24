import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, ArrowRight, UtensilsCrossed } from "lucide-react";
import { getAccessToken } from "../lib/auth";

type Passenger = {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  passenger_type: "adult" | "child";
  seat_number: string;
  food_item_ids?: number[];
};

type CheckoutData = {
  flight_id: number;
  contact_email: string;
  contact_phone: string;
  passengers: Passenger[];
};

type FoodItem = {
  id: number;
  name: string;
  description: string;
  category: string;
  price: string;
  is_available: boolean;
};

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function FoodSelectionPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const checkout = (location.state as { checkout?: CheckoutData } | null)?.checkout;

  const [menu, setMenu] = useState<FoodItem[]>([]);
  const [selections, setSelections] = useState<number[][]>(
    checkout?.passengers.map(() => []) ?? []
  );
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    fetch(`${API_BASE}/api/v1/food`)
      .then(async (response) => {
        if (!response.ok) throw new Error("Unable to load food menu.");
        return (await response.json()) as FoodItem[];
      })
      .then((items) => {
        if (active) setMenu(items);
      })
      .catch((err) => {
        if (active) setError(err instanceof Error ? err.message : "Menu unavailable.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const foodTotal = useMemo(() => {
    const prices = new Map(menu.map((item) => [item.id, Number(item.price)]));
    return selections.reduce(
      (total, passengerItems) =>
        total + passengerItems.reduce((sum, id) => sum + (prices.get(id) ?? 0), 0),
      0
    );
  }, [menu, selections]);

  function toggleFood(passengerIndex: number, foodId: number) {
    setSelections((current) =>
      current.map((items, index) =>
        index !== passengerIndex
          ? items
          : items.includes(foodId)
            ? items.filter((id) => id !== foodId)
            : items.length < 10
              ? [...items, foodId]
              : items
      )
    );
  }

  async function createBooking(skipFood: boolean) {
    if (!checkout || submitting) return;

    setSubmitting(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/api/v1/bookings`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(getAccessToken()
            ? { Authorization: `Bearer ${getAccessToken()}` }
            : {}),
        },
        body: JSON.stringify({
          ...checkout,
          passengers: checkout.passengers.map((passenger, index) => ({
            ...passenger,
            food_item_ids: skipFood ? [] : selections[index] ?? [],
          })),
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof result.detail === "string"
            ? result.detail
            : "Unable to create booking."
        );
      }

      navigate(`/booking/${result.id}`, {
        replace: true,
        state: { booking: result },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Booking failed.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!checkout) {
    return (
      <main className="min-h-screen bg-slate-50 p-10 text-center">
        <h1 className="text-2xl font-bold">Checkout session unavailable</h1>
        <p className="mt-3 text-slate-500">
          Please select your flight and seats again.
        </p>
        <button
          onClick={() => navigate("/")}
          className="mt-6 rounded-xl bg-blue-600 px-6 py-3 text-white"
        >
          Back to Home
        </button>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 text-slate-900">
      <div className="mx-auto max-w-4xl">
        <button
          onClick={() => navigate(-1)}
          className="mb-8 flex items-center gap-2 text-slate-600"
        >
          <ArrowLeft size={18} /> Back to seats
        </button>

        <div className="mb-8">
          <div className="mb-3 flex items-center gap-3 text-blue-600">
            <UtensilsCrossed size={28} />
            <span className="font-semibold uppercase tracking-widest">
              AeroSky Extras
            </span>
          </div>
          <h1 className="text-4xl font-bold">Choose your in-flight food</h1>
          <p className="mt-3 text-slate-500">
            Food is optional. Select meals for each passenger or skip at no extra cost.
          </p>
        </div>

        {loading && <p className="mb-6">Loading food menu...</p>}

        {!loading && checkout.passengers.map((passenger, passengerIndex) => (
          <section
            key={passengerIndex}
            className="mb-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <h2 className="mb-5 text-xl font-bold">
              {passenger.first_name} {passenger.last_name}
              <span className="ml-3 text-sm font-normal text-slate-500">
                Seat {passenger.seat_number}
              </span>
            </h2>

            <div className="grid gap-3 sm:grid-cols-2">
              {menu.map((item) => {
                const selected = selections[passengerIndex]?.includes(item.id) ?? false;

                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => toggleFood(passengerIndex, item.id)}
                    aria-pressed={selected}
                    className={`rounded-2xl border p-4 text-left transition ${
                      selected
                        ? "border-blue-600 bg-blue-50"
                        : "border-slate-200 hover:border-blue-300"
                    }`}
                  >
                    <div className="flex justify-between gap-3">
                      <span className="font-semibold">{item.name}</span>
                      <span className="font-bold text-blue-700">
                        ₹{Number(item.price).toLocaleString("en-IN")}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-slate-500">{item.description}</p>
                    <p className="mt-2 text-xs font-semibold text-blue-600">
                      {selected ? "Selected ✓" : "Click to add"}
                    </p>
                  </button>
                );
              })}
            </div>
          </section>
        ))}

        {error && (
          <p role="alert" className="mb-5 rounded-xl bg-red-50 p-4 text-red-700">
            {error}
          </p>
        )}

        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex justify-between text-xl font-bold">
            <span>Food total</span>
            <span>₹{foodTotal.toLocaleString("en-IN")}</span>
          </div>
          <p className="mb-5 text-sm text-slate-500">
            The final booking amount will be calculated securely by AeroSky.
          </p>

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              disabled={submitting}
              onClick={() => createBooking(true)}
              className="flex-1 rounded-2xl border border-slate-300 px-6 py-4 font-semibold hover:bg-slate-50 disabled:opacity-50"
            >
              Skip Food — ₹0
            </button>

            <button
              type="button"
              disabled={loading || submitting || Boolean(error)}
              onClick={() => createBooking(false)}
              className="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-blue-600 px-6 py-4 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? "Creating booking..." : "Continue to Payment"}
              <ArrowRight size={18} />
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
