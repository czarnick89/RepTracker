import { useState } from "react";
import api from '../api/axiosRefreshInterceptor';
import { Link } from "react-router-dom";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [registered, setRegistered] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      const response = await api.post(
        "https://localhost:8000/api/v1/users/register/",
        {
          email,
          password,
        }
      );

      console.log("Registration successful:", response.data);
      setSuccess(
        "Registration successful! Check your email to verify your account."
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
            Registration successful! Check your email to verify your account before logging in.
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
            {password && password.length < 8 && (
              <p className="text-orange-500 text-sm mt-1">
                Password must be at least 8 characters.
              </p>
            )}
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-700">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="mt-1 w-full px-4 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
          >
            Register
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
