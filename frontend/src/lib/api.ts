import { getAccessToken } from "./auth";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function apiGet<T>(
  endpoint: string,
  signal?: AbortSignal
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "GET",
    signal,
    headers: {
      Accept: "application/json",
      ...(getAccessToken()
        ? { Authorization: `Bearer ${getAccessToken()}` }
        : {}),
    },
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const error = await response.json();
      if (typeof error.detail === "string") {
        message = error.detail;
      }
    } catch {
      // Keep the fallback message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}
