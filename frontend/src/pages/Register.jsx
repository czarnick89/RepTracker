import { useState, useRef } from "react";
import api from "../api/axiosRefreshInterceptor";
import { Link } from "react-router-dom";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [registered, setRegistered] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const submittingRef = useRef(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // prevent duplicate submissions (covers very fast double-clicks)
    if (submittingRef.current) return;
    submittingRef.current = true;
    setIsSubmitting(true);

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      submittingRef.current = false;
      setIsSubmitting(false);
      return;
    }

    try {
      await api.post(
        `${import.meta.env.VITE_BACKEND_URL}/api/v1/users/register/`,
        {
          email,
          password,
        }
      );

      setRegistered(true);
      setEmail("");
      setPassword("");
      setConfirmPassword("");
    } catch (err) {
      console.error("Registration failed:", err.response?.data || err.message);

      if (err.response?.data?.password) {
        setError(
          `Registration failed: Password ${err.response.data.password
            .join(" ")
            .toLowerCase()}`
        );
      } else if (err.response?.data?.email) {
        setError(`Registration failed: ${err.response.data.email.join(" ")}`);
      } else {
        setError("Registration failed. Check your input.");
      }
    } finally {
      submittingRef.current = false;
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-slate-900 min-h-screen flex items-center justify-center px-4">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-slate-800">
          RepTracker Register
        </h2>

        {error && (
          <p className="text-red-600 text-sm mb-4 text-center">{error}</p>
        )}

        {registered ? (
          <>
            <p className="text-green-600 text-sm mb-4 text-center">
              Registration successful! Check your email to verify your account
              before logging in.
            </p>
            <p className="text-center">
              <Link to="/login" className="text-blue-600 hover:underline">
                Go to Login
              </Link>
            </p>
          </>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-slate-700"
              >
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

            <div className="relative">
              <label
                htmlFor="password"
                className="block text-sm font-medium text-slate-700"
              >
                Password
              </label>
              <div className="text-sm text-slate-600 mt-1 mb-2">
                <ul className="list-disc list-inside ml-4 mt-1">
                  <li>At least 8 characters</li>
                  <li>Not entirely numeric</li>
                </ul>
              </div>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pr-16 px-4 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-sm text-slate-600 hover:text-slate-800"
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
              <p className="text-sm mt-1">
                <span className={password ? (password.length >= 8 ? "text-green-600" : "text-red-600") : "text-slate-400"}>
                  {password ? (password.length >= 8 ? "✓" : "✗") : "○"} At least 8 characters
                </span>
                <br />
                <span className={password ? (!/^\d+$/.test(password) ? "text-green-600" : "text-red-600") : "text-slate-400"}>
                  {password ? (!/^\d+$/.test(password) ? "✓" : "✗") : "○"} Not entirely numeric
                </span>
              </p>
            </div>

            <div className="relative">
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-slate-700"
              >
                Confirm Password
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="mt-1 w-full pr-16 px-4 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-sm text-slate-600 hover:text-slate-800"
                >
                  {showConfirmPassword ? "Hide" : "Show"}
                </button>
              </div>
              <p className="text-green-600 text-sm mt-1">
                {confirmPassword && password === confirmPassword ? "✓ Passwords match" : "\u00A0"}
              </p>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full py-2 px-4 bg-blue-600 text-white rounded-md transition ${
                isSubmitting ? "opacity-60 cursor-not-allowed" : "hover:bg-blue-700"
              }`}
            >
              {isSubmitting ? "Registering..." : "Register"}
            </button>
          </form>
        )}

        <div className="mt-4 text-sm text-center">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-600 hover:underline">
            Log in here
          </Link>
        </div>
      </div>
    </div>
  );
}
