import { useState } from "react";
import axios from "axios";
import { Link, useNavigate, useLocation, Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, loading: authLoading, setUser } = useAuth();

  // Redirect logged-in users away from login page
  if (!authLoading && user) {
    const from = location.state?.from?.pathname || "/dashboard";
    return <Navigate to={from} replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Step 1: Login
      await axios.post(
        "https://127.0.0.1:8000/api/v1/users/login/",
        { email, password },
        { withCredentials: true }
      );

      // Step 2: Fetch user profile
      const res = await axios.get(
        "https://127.0.0.1:8000/api/v1/users/profile/",
        { withCredentials: true }
      );

      // Step 3: Set user in AuthContext
      setUser(res.data);

      // Step 4: Redirect to intended page or dashboard
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
    <div style={{ maxWidth: "400px", margin: "2rem auto" }}>
      <h2>RepTrack Login</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="email">Email:</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: "100%", padding: "0.5rem" }}
          />
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="password">Password:</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%", padding: "0.5rem" }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "0.5rem 1rem",
            marginBottom: "1rem",
            opacity: loading ? 0.6 : 1,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Logging in..." : "Log In"}
        </button>
      </form>

      <p
        style={{
          marginBottom: "0.5rem",
          textAlign: "center",
          cursor: "pointer",
          color: "blue",
        }}
      >
        Forgot Password?
      </p>

      <Link
        to="/register"
        style={{
          textAlign: "center",
          display: "block",
          color: "blue",
        }}
      >
        Create Account
      </Link>
    </div>
  );
}
