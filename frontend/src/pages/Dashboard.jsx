import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useState } from "react";

export default function Dashboard() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    navigate("/logout");
  };

  const handleToggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleCloseSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="relative min-h-screen bg-blue-900 text-white">
      {/* Navbar */}
      <nav className="bg-gray-800 text-white p-4 flex items-center justify-center relative">
        {/* Hamburger positioned absolutely on left */}
        <button
          onClick={handleToggleSidebar}
          className="text-white text-2xl focus:outline-none absolute left-4"
          aria-label="Toggle Menu"
        >
          &#9776;
        </button>

        {/* Logo / Title centered */}
        <Link
          to="/dashboard"
          className="text-xl font-bold hover:text-gray-300"
          onClick={handleCloseSidebar}
        >
          RepTrack Dashboard
        </Link>
      </nav>

      {/* Sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-gray-900/50 z-40"
          onClick={handleCloseSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full bg-gray-900 text-white z-40 transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
      `}
        style={{ width: "50vw", maxWidth: "300px" }}
      >
        <div className="p-6 flex flex-col space-y-6">
          <Link
            to="/dashboard"
            className="hover:text-gray-400 text-lg font-semibold"
            onClick={handleCloseSidebar}
          >
            Dashboard
          </Link>
          <Link
            to="/profile"
            className="hover:text-gray-400 text-lg font-semibold"
            onClick={handleCloseSidebar}
          >
            Profile
          </Link>
          <Link
            to="/analytics"
            className="hover:text-gray-400 text-lg font-semibold"
            onClick={handleCloseSidebar}
          >
            Analytics
          </Link>
          <Link
            to="/settings"
            className="hover:text-gray-400 text-lg font-semibold"
            onClick={handleCloseSidebar}
          >
            Settings
          </Link>
          <Link
            to="/search"
            className="hover:text-gray-400 text-lg font-semibold"
            onClick={handleCloseSidebar}
          >
            Search
          </Link>
          <button
            onClick={() => {
              handleCloseSidebar();
              handleLogout();
            }}
            className="mt-auto bg-red-600 px-4 py-2 rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="p-10 text-center">

  <button
    onClick={() => (window.location.href = "/workouts/new")}
    className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 transition"
  >
    Create New Workout
  </button>

  {/* You can add other dashboard content here */}
</main>

    </div>
  );
}
