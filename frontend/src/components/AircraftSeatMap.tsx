import { useQuery } from "@tanstack/react-query";
import { apiGet } from "../lib/api";

type Seat = {
  seat_number: string;
  row: number;
  column: string;
  cabin_class: string;
  status: "available" | "held" | "booked";
};

type SeatMapResponse = {
  flight_id: number;
  flight_number: string;
  aircraft: {
    name: string;
    model: string;
    total_seats: number;
  };
  available_seats: number;
  seats: Seat[];
};

type Props = {
  flightId: number;
  passengerCount: number;
  selectedSeats: string[];
  onChange: (seats: string[]) => void;
};

export default function AircraftSeatMap({
  flightId,
  passengerCount,
  selectedSeats,
  onChange,
}: Props) {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["seat-map", flightId],
    queryFn: () =>
      apiGet<SeatMapResponse>(`/api/v1/flights/${flightId}/seats`),
    refetchInterval: 15000,
  });

  function selectSeat(seat: Seat) {
    if (seat.status !== "available") return;

    if (selectedSeats.includes(seat.seat_number)) {
      onChange(selectedSeats.filter((s) => s !== seat.seat_number));
      return;
    }

    if (selectedSeats.length >= passengerCount) return;

    onChange([...selectedSeats, seat.seat_number]);
  }

  if (isLoading) {
    return (
      <section className="rounded-3xl bg-white p-8 text-center shadow-sm">
        Loading aircraft seat map...
      </section>
    );
  }

  if (isError || !data) {
    return (
      <section className="rounded-3xl bg-white p-8 text-center shadow-sm">
        <p className="text-red-600">Unable to load aircraft seats.</p>
        <button
          type="button"
          onClick={() => void refetch()}
          className="mt-4 rounded-xl bg-blue-600 px-5 py-2 text-white"
        >
          Retry
        </button>
      </section>
    );
  }

  const rows = Array.from(
    new Set(data.seats.map((seat) => seat.row))
  ).sort((a, b) => a - b);

  const columns = Array.from(
    new Set(data.seats.map((seat) => seat.column))
  ).sort();

  const middle = Math.ceil(columns.length / 2);

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8">
      <div className="mb-6">
        <p className="text-xs font-semibold uppercase tracking-widest text-blue-600">
          Aircraft seat selection
        </p>
        <h2 className="mt-2 text-2xl font-bold">
          Choose your seats
        </h2>
        <p className="mt-2 text-sm text-slate-500">
          {data.aircraft.name} · {data.flight_number}
        </p>
        <p className="mt-2 text-sm font-medium text-blue-700">
          Selected {selectedSeats.length} of {passengerCount} seats
        </p>
      </div>

      <div className="mb-8 flex flex-wrap gap-4 text-xs">
        <span className="flex items-center gap-2">
          <span className="h-4 w-4 rounded bg-emerald-100 ring-1 ring-emerald-400" />
          Available
        </span>
        <span className="flex items-center gap-2">
          <span className="h-4 w-4 rounded bg-blue-600" />
          Selected
        </span>
        <span className="flex items-center gap-2">
          <span className="h-4 w-4 rounded bg-slate-300" />
          Occupied / held
        </span>
      </div>

      <div className="overflow-x-auto rounded-2xl bg-slate-50 p-4">
        <div className="mx-auto w-max rounded-t-[90px] border-x-4 border-t-4 border-slate-300 bg-white px-5 pb-10 pt-14 shadow-inner sm:px-9">
          <div className="mb-8 text-center">
            <div className="mx-auto mb-3 h-1 w-20 rounded bg-slate-300" />
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">
              Cockpit
            </p>
          </div>

          <div className="space-y-2">
            {rows.map((row) => (
              <div key={row} className="flex items-center gap-1.5">
                {columns.map((column, index) => {
                  const seat = data.seats.find(
                    (item) => item.row === row && item.column === column
                  );

                  const selected =
                    seat && selectedSeats.includes(seat.seat_number);

                  const unavailable = !seat || seat.status !== "available";

                  return (
                    <div
                      key={`${row}-${column}`}
                      className={index === middle ? "ml-8" : ""}
                    >
                      {seat ? (
                        <button
                          type="button"
                          disabled={unavailable}
                          onClick={() => selectSeat(seat)}
                          title={`${seat.seat_number} · ${seat.cabin_class} · ${seat.status}`}
                          aria-label={`Seat ${seat.seat_number}, ${
                            selected ? "selected" : seat.status
                          }`}
                          aria-pressed={Boolean(selected)}
                          className={`flex h-9 w-9 items-center justify-center rounded-lg border text-[11px] font-bold transition ${
                            selected
                              ? "border-blue-700 bg-blue-600 text-white"
                              : unavailable
                              ? "cursor-not-allowed border-slate-300 bg-slate-300 text-slate-500"
                              : "border-emerald-400 bg-emerald-50 text-emerald-800 hover:bg-emerald-200"
                          }`}
                        >
                          {column}
                        </button>
                      ) : (
                        <div className="h-9 w-9" />
                      )}
                    </div>
                  );
                })}
                <span className="ml-3 w-7 text-center text-xs font-semibold text-slate-400">
                  {row}
                </span>
              </div>
            ))}
          </div>

          <div className="mt-10 border-t border-dashed border-slate-200 pt-5 text-center text-xs text-slate-400">
            Rear cabin
          </div>
        </div>
      </div>

      <div className="mt-6 rounded-2xl bg-blue-50 p-5">
        <h3 className="font-semibold text-blue-900">
          Your selected seats
        </h3>

        {selectedSeats.length === 0 ? (
          <p className="mt-2 text-sm text-blue-700">
            Click an available seat to select it.
          </p>
        ) : (
          <div className="mt-3 flex flex-wrap gap-2">
            {selectedSeats.map((seat, index) => (
              <span
                key={seat}
                className="rounded-lg bg-white px-3 py-2 text-sm font-semibold text-blue-700"
              >
                Passenger {index + 1}: {seat}
              </span>
            ))}
          </div>
        )}
      </div>

      <p className="mt-4 text-xs text-slate-500">
        Seat choices are currently a preview and are not reserved until
        backend seat assignment is implemented.
      </p>
    </section>
  );
}
