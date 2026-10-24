import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import {
  clearAccessToken,
  getAccessToken,
  isTokenExpired,
  saveAccessToken,
} from "../lib/auth";

type AuthContextValue = {
  isAuthenticated: boolean;
  token: string | null;
  login: (accessToken: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(
  undefined
);

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [token, setToken] = useState<string | null>(
    () => getAccessToken()
  );

  useEffect(() => {
    if (!token) return;

    if (isTokenExpired(token)) {
      clearAccessToken();
      setToken(null);
      return;
    }

    // Recheck periodically so React updates after token expiry.
    const interval = window.setInterval(() => {
      if (!getAccessToken()) {
        clearAccessToken();
        setToken(null);
      }
    }, 5000);

    return () => window.clearInterval(interval);
  }, [token]);

  useEffect(() => {
    function handleSessionExpired() {
      setToken(getAccessToken());
    }

    window.addEventListener(
      "aerosky:session-expired",
      handleSessionExpired
    );

    return () => {
      window.removeEventListener(
        "aerosky:session-expired",
        handleSessionExpired
      );
    };
  }, []);

  function login(accessToken: string) {
    saveAccessToken(accessToken);
    setToken(accessToken);
  }

  function logout() {
    clearAccessToken();
    setToken(null);
  }

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: Boolean(token),
        token,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}
