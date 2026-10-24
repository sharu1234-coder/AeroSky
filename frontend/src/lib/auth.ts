const TOKEN_KEY = "aerosky_access_token";

type JwtPayload = {
  exp?: number;
};

export function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split(".");

    if (parts.length !== 3) {
      return true;
    }

    const base64 = parts[1]
      .replace(/-/g, "+")
      .replace(/_/g, "/");

    const payload = JSON.parse(
      atob(base64)
    ) as JwtPayload;

    if (
      typeof payload.exp !== "number" ||
      !Number.isFinite(payload.exp)
    ) {
      return true;
    }

    return Date.now() >= payload.exp * 1000;
  } catch {
    return true;
  }
}

export function getAccessToken(): string | null {
  const token = sessionStorage.getItem(TOKEN_KEY);

  if (!token) {
    return null;
  }

  if (isTokenExpired(token)) {
    sessionStorage.removeItem(TOKEN_KEY);
    return null;
  }

  return token;
}

export function saveAccessToken(token: string): void {
  if (isTokenExpired(token)) {
    throw new Error("Invalid or expired login token.");
  }

  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  sessionStorage.removeItem(TOKEN_KEY);
}
