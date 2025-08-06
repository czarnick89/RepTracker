import { useNavigate } from "react-router-dom";

export default function DashboardPage() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      const response = await fetch("https://127.0.0.1:8000/api/v1/users/logout/", {
        method: "POST",
        credentials: "include", // Send cookies
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        navigate("/"); // Go back to landing page
      } else {
        console.error("Logout failed");
      }
    } catch (error) {
      console.error("Error during logout:", error);
    }
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
