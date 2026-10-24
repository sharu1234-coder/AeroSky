import FoodSelectionPage from "./pages/FoodSelectionPage";
import MyBookingsPage from "./pages/MyBookingsPage";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import { AuthProvider } from "./context/AuthContext";
import PassengerDetailsPage from "./pages/PassengerDetailsPage";
import BookingSummaryPage from "./pages/BookingSummaryPage";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import HomePage from "./pages/HomePage";
import FlightResultsPage from "./pages/FlightResultsPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/flights" element={<FlightResultsPage />} />

          <Route path="/checkout/:flightId" element={<ProtectedRoute><PassengerDetailsPage /></ProtectedRoute>} />
          <Route path="/checkout/food" element={<ProtectedRoute><FoodSelectionPage /></ProtectedRoute>} />
          <Route path="/booking/:bookingId" element={<ProtectedRoute><BookingSummaryPage /></ProtectedRoute>} />

        <Route
          path="/my-bookings"
          element={
            <ProtectedRoute>
              <MyBookingsPage />
            </ProtectedRoute>
          }
        />
</Routes>
      </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
