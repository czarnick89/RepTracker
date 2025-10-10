import { useState } from "react";
import api from '../api/axiosRefreshInterceptor'
import { Link, useNavigate, useLocation, Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Login() {
  // Local state for form inputs, error messages, and loading state
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Hooks for navigation and location (to redirect back after login)
  const navigate = useNavigate();
  const location = useLocation();

  // Auth context: current user info and loading status
  const { user, loading: authLoading, setUser } = useAuth();

  // Redirect logged-in users away from login page
  // Uses location.state.from to send user back to the page they tried to access
  if (!authLoading && user && !import.meta.env.CI) {
    const from = location.state?.from?.pathname || "/dashboard"; // Default to dashboard if the from is unable to be resolved
    return <Navigate to={from} replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Send login request to backend via api
      await api.post(
        `${import.meta.env.VITE_BACKEND_URL}/api/v1/users/login/`,
        { email, password }
      );

      // Fetch user profile after successful login
      const res = await api.get(
        `${import.meta.env.VITE_BACKEND_URL}/api/v1/users/profile/`
      );
      // Update authcontext with user data
      setUser(res.data);
      // Redirect to original page or dashboard
      const from = location.state?.from?.pathname || "/dashboard";
      navigate(from, { replace: true });
    } catch (err) {
      console.error("Login failed:", err.response?.data || err.message);
      const backendMsg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Login failed. Check your email and password.";
      setError(backendMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 min-h-screen flex items-center justify-center px-4">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-slate-800">
          RepTracker Login
        </h2>

        {error && (
          <p className="text-red-600 text-sm mb-4 text-center">{error}</p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 w-full px-4 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 w-full px-4 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition ${
              loading ? "opacity-60 cursor-not-allowed" : ""
            }`}
          >
            {loading ? "Logging in..." : "Log In"}
          </button>
        </form>

        <div className="mt-4 text-sm text-center">
          <Link to="/forgot-password" className="text-blue-600 hover:underline block mb-2">
            Forgot Password?
          </Link>
          <Link to="/register" className="text-blue-600 hover:underline">
            Create Account
          </Link>
        </div>
      </div>
    </div>
  );
}
