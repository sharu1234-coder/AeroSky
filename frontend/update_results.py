from pathlib import Path

path = Path("src/pages/FlightResultsPage.tsx")
source = path.read_text(encoding="utf-8-sig")

if 'const tripType = params.get("trip_type")' in source:
    raise SystemExit("Round-trip information already added.")

backup = path.with_suffix(".tsx.bak")
backup.write_text(source, encoding="utf-8")

old = '  const cabinClass = params.get("cabin_class") ?? "economy";'
new = old + '''
  const tripType = params.get("trip_type") ?? "one-way";
  const returnDate = params.get("return_date") ?? "";
'''

if source.count(old) != 1:
    raise RuntimeError("Could not find cabinClass declaration.")

source = source.replace(old, new, 1)

marker = '        <div className="mb-5 flex flex-wrap items-center justify-between gap-4">'

notice = '''        {tripType === "round-trip" && (
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

'''

if source.count(marker) != 1:
    raise RuntimeError("Could not find results toolbar.")

source = source.replace(marker, notice + marker, 1)

path.write_text(source, encoding="utf-8")
print("Round-trip information added successfully!")
