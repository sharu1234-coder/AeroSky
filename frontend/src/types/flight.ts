export interface Airport {
  id: number;
  code: string;
  name: string;
  city: string;
  country: string;
}

export interface Airline {
  id: number;
  code: string;
  name: string;
}

export interface Flight {
  id: number;
  flight_number: string;
  airline: Airline;
  origin: Airport;
  destination: Airport;
  departure_time: string;
  arrival_time: string;
  price: string;
  available_seats: number;
  cabin_class: string;
}

export interface FlightSearchParams {
  origin: string;
  destination: string;
  departure_date: string;
  passengers: number;
  cabin_class: string;
}
