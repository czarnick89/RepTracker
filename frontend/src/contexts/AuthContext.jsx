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
      try {
        // Attempt to refresh JWT tokens via backend endpoint
        await api.post("/api/v1/users/token/refresh/");

        // If refresh succeeds, fetch the user's profile
        const res = await api.get("/api/v1/users/profile/", {
          headers: { "Cache-Control": "no-cache" },
        });

        if (isMounted) setUser(res.data); // Set user state
      } catch (err) {
        if (isMounted) setUser(null); // Reset user if refresh/profile fetch fails
      } finally {
        if (isMounted) setLoading(false); // Loading complete
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
