import { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../contexts/AuthContext";

export default function Profile() {
  const { user, loading } = useAuth();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (loading) return; // Still loading, do nothing
    if (!user) return; // No user, do nothing and avoid request

    // Only here if user is authenticated and loading is done
    axios
      .get("https://127.0.0.1:8000/api/v1/users/profile/", {
        withCredentials: true,
        headers: { "Cache-Control": "no-cache" },
      })
      .then((res) => setProfile(res.data))
      .catch(() => setError("Failed to load profile."));
  }, [loading, user]);

  if (loading) return <p>Checking authentication...</p>;

  if (!user) return null; // Or maybe <Navigate to="/login" /> if you want direct redirect here

  if (error) return <p className="text-red-500">{error}</p>;

  if (!profile) return <p>Loading profile...</p>;

  return (
    <div className="p-4 rounded bg-gray-100 shadow">
      <h2 className="text-xl font-bold mb-2">User Profile</h2>
      <p>
        <strong>Username:</strong> {profile.username}
      </p>
      <p>
        <strong>Email:</strong> {profile.email}
      </p>
      <button
        onClick={() => (window.location.href = "/logout")}
        className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
      >
        Logout
      </button>
    </div>
  );
}
