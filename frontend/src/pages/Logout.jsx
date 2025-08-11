import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { performLogout } from "../utils/logout";

export default function Logout() {
  const { setUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    performLogout(setUser, navigate);
  }, [setUser, navigate]);

  return <p className="text-center mt-10">Logging you out...</p>;
}
