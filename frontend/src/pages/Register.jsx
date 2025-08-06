import { useState } from "react";
import axios from "axios";
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
      const response = await axios.post(
        "http://localhost:8000/api/v1/users/register/",
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
    <div style={{ maxWidth: "400px", margin: "2rem auto" }}>
      <h2>RepTrack Register</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}

      {registered ? (
        <>
          <p style={{ color: "green" }}>
            Registration successful! Check your email to verify your account before logging in.
          </p>
          <p style={{ marginTop: "1rem", textAlign: "center" }}>
            <Link to="/" style={{ color: "blue", cursor: "pointer" }}>
              Go to Login
            </Link>
          </p>
        </>
      ) : (
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "1rem" }}>
            <label>Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{ width: "100%", padding: "0.5rem" }}
            />
          </div>
          <div style={{ marginBottom: "1rem" }}>
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: "100%", padding: "0.5rem" }}
            />
            {password && password.length < 8 && (
              <p
                style={{
                  color: "orange",
                  fontSize: "0.875rem",
                  marginTop: "0.25rem",
                }}
              >
                Password must be at least 8 characters.
              </p>
            )}
          </div>
          <div style={{ marginBottom: "1rem" }}>
            <label>Confirm Password:</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              style={{ width: "100%", padding: "0.5rem" }}
            />
          </div>
          <button type="submit" style={{ padding: "0.5rem 1rem" }}>
            Register
          </button>
          <p style={{ marginTop: "1rem", textAlign: "center" }}>
            Already have an account?{" "}
            <Link to="/" style={{ color: "blue", cursor: "pointer" }}>
              Log in here
            </Link>
          </p>
        </form>
      )}
    </div>
  );
}
