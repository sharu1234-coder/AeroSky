from dataclasses import dataclass


@dataclass(frozen=True)
class CabinSection:
    cabin_class: str
    start_row: int
    end_row: int
    seat_groups: tuple[str, ...]


AIRCRAFT_LAYOUTS = {
    "A320-ECO": (
        CabinSection("economy", 1, 30, ("ABC", "DEF")),
    ),
    "A320": (
        CabinSection("business", 1, 3, ("AC", "DF")),
        CabinSection("economy", 4, 30, ("ABC", "DEF")),
    ),
    "B787": (
        CabinSection("business", 1, 6, ("A", "DE", "K")),
        CabinSection("premium_economy", 7, 11, ("AC", "DEF", "HK")),
        CabinSection("economy", 12, 40, ("ABC", "DEF", "HJK")),
    ),
    "A350": (
        CabinSection("first", 1, 2, ("A", "DE", "K")),
        CabinSection("business", 3, 10, ("A", "DE", "K")),
        CabinSection("premium_economy", 11, 16, ("AC", "DEF", "HK")),
        CabinSection("economy", 17, 45, ("ABC", "DEF", "HJK")),
    ),
}


def generate_seat_layout(aircraft_model: str) -> list[dict]:
    sections = AIRCRAFT_LAYOUTS.get(aircraft_model)

    if sections is None:
        raise ValueError(f"Unsupported aircraft model: {aircraft_model}")

    seats = []

    for section in sections:
        for row in range(section.start_row, section.end_row + 1):
            for group in section.seat_groups:
                for column in group:
                    seats.append(
                        {
                            "seat_number": f"{row}{column}",
                            "seat_row": row,
                            "seat_column": column,
                            "cabin_class": section.cabin_class,
                            "status": "available",
                        }
                    )

    numbers = [seat["seat_number"] for seat in seats]

    if len(numbers) != len(set(numbers)):
        raise ValueError("Duplicate seat numbers detected.")

    return seats
