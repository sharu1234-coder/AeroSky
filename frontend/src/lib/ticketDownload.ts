import { getAccessToken } from "./auth";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function downloadBookingTicket(
  bookingId: number
): Promise<void> {
  const token = getAccessToken();

  if (!token) {
    throw new Error("Please log in to download your ticket.");
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/bookings/${bookingId}/ticket`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/pdf",
      },
    }
  );

  if (!response.ok) {
    let message = `Ticket download failed (${response.status}).`;

    try {
      const error = await response.json();

      if (typeof error.detail === "string") {
        message = error.detail;
      }
    } catch {
      // Keep fallback error.
    }

    throw new Error(message);
  }

  const blob = await response.blob();

  if (!blob.type.includes("pdf")) {
    throw new Error("Server did not return a PDF document.");
  }

  const url = URL.createObjectURL(blob);

  try {
    const link = document.createElement("a");
    link.href = url;
    link.download = `AeroSky-Demo-Ticket-${bookingId}.pdf`;

    document.body.appendChild(link);
    link.click();
    link.remove();
  } finally {
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
}
