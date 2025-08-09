import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import api from '../api/axiosRefreshInterceptor';

export default function Logout() {
  const { setUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const logout = async () => {
      try {
        await api.post('https://127.0.0.1:8000/api/v1/users/logout/'); // Uses baseURL + credentials automatically
      } catch (err) {
        console.error("Logout error:", err);
      }

      setUser(null);
      navigate("/"); // redirect to Landing
    };

    logout();
  }, [setUser, navigate]);

  return <p className="text-center mt-10">Logging you out...</p>;
}
