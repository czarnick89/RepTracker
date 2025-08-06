import { useEffect, useState } from "react";
import axios from "axios";

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get("https://127.0.0.1:8000/api/v1/users/profile/", {
      withCredentials: true
    })
    .then(res => {
      setProfile(res.data);
    })
    .catch(err => {
      console.error("Profile fetch failed:", err);
      setError("Failed to load profile. Are you logged in?");
    });
  }, []);

  if (error) return <p className="text-red-500">{error}</p>;
  if (!profile) return <p>Loading profile...</p>;

  return (
    <div className="p-4 rounded bg-gray-100 shadow">
      <h2 className="text-xl font-bold mb-2">User Profile</h2>
      <p><strong>Username:</strong> {profile.username}</p>
      <p><strong>Email:</strong> {profile.email}</p>
      {/* Add more fields if your serializer includes them */}
    </div>
  );
}
