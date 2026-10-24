import { clearAccessToken, getAccessToken } from "./auth";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export class AuthenticationError extends Error {
  constructor() {
    super("Your session has expired. Please log in again.");
    this.name = "AuthenticationError";
  }
}

export async function authenticatedFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getAccessToken();

  if (!token) {
    clearAccessToken();
    window.dispatchEvent(new Event("aerosky:session-expired"));
    throw new AuthenticationError();
  }

  const headers = new Headers(options.headers);
  headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...options,
      headers,
    }
  );

  if (response.status === 401) {
    // Clear only the token used by this request.
    // A newer login must not be invalidated by an older request.
    if (getAccessToken() === token) {
      clearAccessToken();
      window.dispatchEvent(new Event("aerosky:session-expired"));
    }

    throw new AuthenticationError();
  }

  return response;
}

export async function readApiError(
  response: Response,
  fallback: string
): Promise<string> {
  try {
    const data: unknown = await response.json();

    if (
      typeof data === "object" &&
      data !== null &&
      "detail" in data &&
      typeof data.detail === "string"
    ) {
      return data.detail;
    }
  } catch {
    // Preserve the fallback.
  }

  return fallback;
}
