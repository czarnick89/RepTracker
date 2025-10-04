import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/axiosRefreshInterceptor";

// Create a React context for auth state
const AuthContext = createContext(null);

// Provider component wrapping the app to provide auth state
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // Stores current user info
  const [loading, setLoading] = useState(true); // Indicates if auth state is being initialized

  useEffect(() => {
    let isMounted = true; // Track if component is still mounted to avoid state updates on unmounted component

    const initializeAuth = async () => {
      // If the interceptor recently forced a logout, skip trying refresh/profile
      try {
        const t = sessionStorage.getItem("auth:interceptor_logout");
        if (t) {
          const ts = Number(t);
          // If logout was forced within last 5 seconds, don't attempt refresh
          // (short cooldown prevents an immediate retry loop between interceptor-forced
          // logout and AuthContext-triggered refresh attempts)
          if (!Number.isNaN(ts) && Date.now() - ts < 5000) {
            if (isMounted) {
              setUser(null);
              setLoading(false);
            }
            return;
          }
        }
      } catch (e) {
        // ignore sessionStorage failures and continue
      }
      try {
        // First attempt: try to fetch the user's profile directly.
        // If the access token is still valid (e.g. stored as a cookie), this will succeed
        // and we avoid calling the refresh endpoint unnecessarily.
        const res = await api.get("/api/v1/users/profile/", {
          headers: { "Cache-Control": "no-cache" },
        });

        if (isMounted) {
          setUser(res.data);
          setLoading(false);
          try {
            sessionStorage.removeItem("auth:interceptor_logout");
          } catch (e) {
            /* ignore */
          }
        }
      } catch (err) {
        // If profile fetch failed with 401, try a refresh flow (refresh token in cookie)
        if (err.response?.status === 401) {
          try {
            await api.post("/api/v1/users/token/refresh/");
            // After successful refresh, fetch profile again
            const res2 = await api.get("/api/v1/users/profile/", {
              headers: { "Cache-Control": "no-cache" },
            });
            if (isMounted) setUser(res2.data);
            try {
              sessionStorage.removeItem("auth:interceptor_logout");
            } catch (e) {
              /* ignore */
            }
          } catch (err2) {
            // Refresh failed or profile fetch still failed: treat as unauthenticated
            if (isMounted) setUser(null);
          } finally {
            if (isMounted) setLoading(false);
          }
        } else {
          // Other errors (network, 5xx, etc.) - clear user and stop loading
          if (isMounted) {
            setUser(null);
            setLoading(false);
          }
        }
      }
    };

    initializeAuth();

    // Cleanup to prevent memory leaks
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    // Provide user, setUser, and loading state to any component consuming this context
    <AuthContext.Provider value={{ user, setUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook for convenient access to auth context
export const useAuth = () => useContext(AuthContext);
