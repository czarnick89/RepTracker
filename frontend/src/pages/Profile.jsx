import { useEffect, useState } from "react";
import api from "../api/axiosRefreshInterceptor";
import { useAuth } from "../contexts/AuthContext";
import ChangePasswordForm from "../components/ChangePasswordForm";

export default function Profile() {
  const { user, loading } = useAuth();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const [googleCalendarConnected, setGoogleCalendarConnected] = useState(false);

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    date: "",
    startTime: "",
    endTime: "",
    location: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const startDateTime = new Date(`${formData.date}T${formData.startTime}`);
    const endDateTime = new Date(`${formData.date}T${formData.endTime}`);

    const payload = {
      summary: formData.title,
      start_time: startDateTime.toISOString(),
      end_time: endDateTime.toISOString(),
      location: formData.location || "",
      description: formData.description || "",
    };

    try {
      await api.post("/api/v1/workouts/google-calendar/create-event/", payload, {
        withCredentials: true,
      });
      alert("Workout scheduled!");
      setFormData({
        title: "",
        description: "",
        date: "",
        startTime: "",
        endTime: "",
        location: "",
      });
    } catch (err) {
      console.error(err);
      alert("Error scheduling workout");
    }
  };

  useEffect(() => {
    if (loading || !user) return;

    const fetchStatus = async () => {
      try {
        const res = await api.get("/api/v1/workouts/google-calendar/status/", {
          withCredentials: true,
          headers: { "Cache-Control": "no-cache" },
        });
        setGoogleCalendarConnected(res.data.connected);
      } catch (err) {
        console.error("Failed to fetch Google Calendar status:", err);
        setGoogleCalendarConnected(false);
      }
    };

    fetchStatus();
  }, [loading, user]);

  useEffect(() => {
    if (loading || !user) return;

    api
      .get("/api/v1/users/profile/", {
        withCredentials: true,
        headers: { "Cache-Control": "no-cache" },
      })
      .then((res) => setProfile(res.data))
      .catch(() => setError("Failed to load profile."));
  }, [loading, user]);

  if (loading) return <p>Checking authentication...</p>;
  if (!user) return null;
  if (error) return <p className="text-red-500">{error}</p>;
  if (!profile) return <p>Loading profile...</p>;

  return (
    <div className="bg-slate-900 min-h-screen flex flex-col md:flex-row items-center justify-center gap-10 px-6 py-12 pt-5">
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-lg shadow-md max-w-md w-full p-6 space-y-5"
      >
        <h2 className="text-2xl font-bold text-slate-800 text-center w-full border-b border-gray-300 pb-3">
          Workout Scheduler
        </h2>
        <input
          type="text"
          name="title"
          placeholder="Workout Title"
          value={formData.title}
          onChange={handleChange}
          className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 transition text-black"
          required
        />
        <input
          type="date"
          name="date"
          value={formData.date}
          onChange={handleChange}
          className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 transition text-black"
          required
        />
        <div className="flex gap-4">
          <input
            type="time"
            name="startTime"
            value={formData.startTime}
            onChange={handleChange}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 transition text-black"
            required
          />
          <input
            type="time"
            name="endTime"
            value={formData.endTime}
            onChange={handleChange}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 transition text-black"
            required
          />
        </div>
        <input
          type="text"
          name="location"
          placeholder="Location"
          value={formData.location}
          onChange={handleChange}
          className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 transition text-black"
        />
        <button
          type="submit"
          className="w-full bg-blue-600 text-white font-semibold py-3 rounded-md hover:bg-blue-700 transition shadow-md"
        >
          Schedule Workout
        </button>
      </form>

      <aside className="bg-white rounded-lg shadow-md p-8 max-w-md w-full flex flex-col items-center space-y-6">
        <h2 className="text-2xl font-bold text-slate-800 text-center w-full border-b border-gray-300 pb-3">
          User Profile
        </h2>

        {!googleCalendarConnected ? (
          <button
            onClick={() => {
              window.location.href =
                "https://127.0.0.1:8000/api/v1/workouts/google-calendar/auth-start/";
            }}
            className="w-full bg-blue-600 text-black py-3 rounded-md hover:bg-blue-700 transition shadow-md"
          >
            Connect Google Calendar
          </button>
        ) : (
          <div className="flex flex-col items-center gap-2 w-full">
            <p className="text-green-600 font-semibold flex items-center gap-2">
              Google Calendar connected <span aria-label="checkmark">✅</span>
            </p>
            <button
              onClick={async () => {
                try {
                  await api.post(
                    "/api/v1/workouts/google-calendar/disconnect/",
                    {},
                    { withCredentials: true }
                  );
                  setGoogleCalendarConnected(false);
                  alert("Google Calendar disconnected");
                } catch (err) {
                  console.error("Failed to disconnect Google Calendar", err);
                  alert("Error disconnecting Google Calendar");
                }
              }}
              className="w-full bg-red-600 text-white py-2 rounded-md hover:bg-red-700 transition shadow-md"
            >
              Disconnect Google Calendar
            </button>
          </div>
        )}

        <div className="w-full space-y-4 text-slate-700">
          <p>
            <span className="font-semibold">Username:</span> {profile.username}
          </p>
          <p>
            <span className="font-semibold">Email:</span> {profile.email}
          </p>
        </div>

        {/* Replace old Change Password form with your component */}
        <ChangePasswordForm />
      </aside>
    </div>
  );
}
