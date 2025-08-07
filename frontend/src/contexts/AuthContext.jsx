// AuthContext.js
import { createContext, useContext, useEffect, useState } from "react";
import axios from "axios";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // Start in loading state

  // Check if user is already authenticated (via cookie) on mount
  useEffect(() => {
    axios
      .get("https://127.0.0.1:8000/api/v1/users/profile/", {
        withCredentials: true,
        headers: { "Cache-Control": "no-cache" },
      })
      .then((res) => {
        setUser(res.data);
      })
      .catch(() => {
        setUser(null);
      })
      .finally(() => setLoading(false)); // Only set loading to false once check is done
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
