import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { performLogout } from "../utils/logout";

// Logout page: logs the user out on mount
export default function Logout() {
  const { setUser } = useAuth(); // Context function to clear user state
  const navigate = useNavigate();

  useEffect(() => {
    // Perform logout when component mounts
    // Clears user state and redirects to login
    performLogout(setUser, navigate);
  }, [setUser, navigate]);

  return <p className="text-center mt-10">Logging you out...</p>;
}
