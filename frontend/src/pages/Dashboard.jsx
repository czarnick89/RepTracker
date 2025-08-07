import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Dashboard() {
  const navigate = useNavigate();
  const { setUser } = useAuth(); // Get setUser from context

  const handleLogout = () => {
    navigate("/logout");
  };

  return (
    <div className="p-10 text-center">
      <h1 className="text-3xl mb-4">DASHBOARD</h1>
      <button
        onClick={handleLogout}
        className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
      >
        Logout
      </button>
    </div>
  );
}
