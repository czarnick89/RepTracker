import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/axiosRefreshInterceptor";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const initializeAuth = async () => {
      try {
        // Try refresh token first
        await api.post("/api/v1/users/token/refresh/");

        // If refresh succeeded, fetch user profile
        const res = await api.get("/api/v1/users/profile/", {
          headers: { "Cache-Control": "no-cache" },
        });

        if (isMounted) setUser(res.data);
      } catch (err) {
        if (isMounted) setUser(null);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    initializeAuth();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
