import { useEffect, useState } from "react";
// import axios from "axios";
import api from '../api/axiosRefreshInterceptor';
import { useAuth } from "../contexts/AuthContext";

export default function Profile() {
  const { user, loading } = useAuth();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (loading) return; // Still loading, do nothing
    if (!user) return; // No user, do nothing and avoid request

    // Only here if user is authenticated and loading is done
    api
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
    <div className="bg-slate-900 min-h-screen flex items-center justify-center px-4">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-slate-800">
          User Profile
        </h2>

        <div className="space-y-3 text-slate-700">
          <p>
            <span className="font-semibold">Username:</span> {profile.username}
          </p>
          <p>
            <span className="font-semibold">Email:</span> {profile.email}
          </p>
        </div>

        <button
          onClick={() => (window.location.href = "/logout")}
          className="mt-6 w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
