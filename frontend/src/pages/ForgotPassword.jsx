import { useState } from "react";
import { Link } from "react-router-dom";
import api from '../api/axiosRefreshInterceptor';

// ForgotPassword page allows users to request a password reset email
export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState(null); 
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus(null);
    setMessage("");
    try {
      const response = await api.post(
        `${import.meta.env.VITE_BACKEND_URL}/api/v1/users/password-reset/`,
        { email },
        {
          headers: {
            "Content-Type": "application/json",
          },
          withCredentials: true,
        }
      );
      setStatus("success");
      setMessage("Password reset email sent. Please check your inbox.");
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail ||
        err.response?.data?.error ||
        "An error occurred. Please try again.";
      setStatus("error");
      setMessage(errorMsg);
    }
  };

  return (
    <div className="bg-slate-900 min-h-screen flex items-center justify-center px-4">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-slate-800">
          Forgot Password
        </h2>

        {status && (
          <p
            className={`text-sm text-center mb-4 ${
              status === "success" ? "text-green-600" : "text-red-600"
            }`}
          >
            {message}
          </p>
        )}

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

          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
          >
            Send Reset Link
          </button>
        </form>

        <div className="mt-4 text-sm text-center space-y-1">
          <Link to="/login" className="text-blue-600 hover:underline block">
            Back to Login
          </Link>
          <Link to="/register" className="text-blue-600 hover:underline block">
            Create Account
          </Link>
        </div>
      </div>
    </div>
  );
}
