import { useState, useEffect } from "react";
import { Link, useNavigate, Outlet, useOutletContext } from "react-router-dom";
import ConfirmModal from "./ConfirmModal";

// Layout component wraps all protected pages and provides Navbar, Sidebar, and Logout functionality
export default function Layout() {
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false); // Sidebar visibility state
  const [logoutModalOpen, setLogoutModalOpen] = useState(false); // Logout confirmation modal state

  // Handles logout click
  const handleLogout = () => {
    navigate("/logout");
  };

  return (
    <div className="min-h-screen bg-blue-900 text-white">
      {/* Navbar */}
      <nav className="bg-gray-800 text-white p-4 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-white text-2xl"
            aria-label="Toggle Menu"
          >
            &#9776;
          </button>

          <Link
            to="/dashboard"
            className="text-xl font-bold hover:text-gray-300 transition-all duration-300"
            onClick={() => setSidebarOpen(false)}
          >
            RepTracker
          </Link>
        </div>

        {/* Placeholder for dashboard buttons - will be populated by Dashboard component */}
        <div id="navbar-actions" className="flex items-center gap-2"></div>
      </nav>

      {/* Sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-gray-900/50 z-40"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full bg-gray-900 text-white z-50 transform transition-transform duration-300 ease-in-out
      ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}
        style={{ width: "50vw", maxWidth: "300px" }}
      >
        <div className="p-6 flex flex-col space-y-6">
          <Link to="/dashboard" onClick={() => setSidebarOpen(false)}>
            Dashboard
          </Link>
          <Link to="/dashboard" onClick={() => setSidebarOpen(false)}>
            Analytics
          </Link>
          <Link to="/profile" onClick={() => setSidebarOpen(false)}>
            Profile
          </Link>
          <button
            onClick={() => setLogoutModalOpen(true)}
            className="text-red-600 border border-red-600 hover:bg-red-600 hover:text-white transition px-3 py-1 rounded text-center"
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Logout modal */}
      <ConfirmModal
        isOpen={logoutModalOpen}
        title="Confirm Logout"
        message="Are you sure you want to log out?"
        onConfirm={() => {
          setLogoutModalOpen(false);
          setSidebarOpen(false);
          handleLogout();
        }}
        onCancel={() => setLogoutModalOpen(false)}
      />

      {/* Page content - add padding-top to account for sticky navbar */}
      <main className="p-5">
        <Outlet />
      </main>
    </div>
  );
}
