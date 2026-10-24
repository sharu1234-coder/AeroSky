from pathlib import Path
import re

path = Path("src/components/FlightSearch.tsx")
source = path.read_text(encoding="utf-8-sig")

if "useNavigate" in source:
    raise SystemExit("FlightSearch already appears to be connected. No changes made.")

backup = path.with_suffix(".tsx.bak")
backup.write_text(source, encoding="utf-8")

def replace_once(old, new):
    global source
    if source.count(old) != 1:
        raise RuntimeError(f"Expected one occurrence: {old[:70]}")
    source = source.replace(old, new, 1)

replace_once(
    'import { useState, type FormEvent, type ReactNode } from "react";',
    'import { useState, type FormEvent, type ReactNode } from "react";\n'
    'import { useNavigate } from "react-router-dom";'
)

# Remove the old preview-only data type.
source, count = re.subn(
    r'type SearchDetails = \{.*?\};\s*',
    '',
    source,
    count=1,
    flags=re.S,
)
if count != 1:
    raise RuntimeError("Could not find SearchDetails type.")

# Remove the preview-only date formatter.
source, count = re.subn(
    r'const formatDate = \(date: string\) =>.*?\n\s*\}\);\s*',
    '',
    source,
    count=1,
    flags=re.S,
)
if count != 1:
    raise RuntimeError("Could not find formatDate.")

replace_once(
    'export default function FlightSearch() {',
    'export default function FlightSearch() {\n'
    '  const navigate = useNavigate();'
)

replace_once(
    '  const [result, setResult] = useState<SearchDetails | null>(null);',
    ''
)

# Remove references to the old preview state.
source = re.sub(r'^\s*setResult\(null\);\s*\n', '', source, flags=re.M)

old_result = '''    setResult({
      from,
      to,
      departure,
      ...(tripType === "round-trip" ? { returnDate } : {}),
      adults,
      children,
      cabin,
      tripType,
    });'''

new_result = '''    const cabinMap: Record<CabinClass, string> = {
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

    navigate(`/flights?${params.toString()}`);'''

replace_once(old_result, new_result)

# Remove the unused cityName function.
source, count = re.subn(
    r'  const cityName = \(code: string\) =>\s*\n'
    r'    airports\.find\(\(airport\) => airport\.code === code\)\?\.city \?\? code;\s*\n',
    '',
    source,
    count=1,
)
if count != 1:
    raise RuntimeError("Could not remove cityName.")

# Remove the old search-preview JSX section.
start = source.find('      {/* SEARCH PREVIEW */}')
if start == -1:
    raise RuntimeError("Could not find search preview.")

end = source.find('\n    </section>', start)
if end == -1:
    raise RuntimeError("Could not find end of component.")

source = source[:start] + source[end:]

path.write_text(source, encoding="utf-8")
print("Homepage search connected successfully!")
print(f"Backup saved: {backup}")
