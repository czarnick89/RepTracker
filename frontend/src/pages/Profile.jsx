import { useEffect, useState } from "react";
import api from "../api/axiosRefreshInterceptor";
import { useAuth } from "../contexts/AuthContext";
import ChangePasswordForm from "../components/ChangePasswordForm";
import Loading from "../components/Loading";

// Profile page component: shows user info, allows password change, and workout scheduling
export default function Profile() {
  const { user, loading } = useAuth(); // Get current user and auth loading state
  const [profile, setProfile] = useState(null); // Stores profile info fetched from backend
  const [error, setError] = useState(null);
  const [googleCalendarConnected, setGoogleCalendarConnected] = useState(false); // Tracks Google Calendar connection status

  // Used to store form data. Default blank
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    date: "",
    startTime: "",
    endTime: "",
    location: "",
  });

  // Handle change on form inputs
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle scheduling form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Formats the inputted times and dates into strings
    const startDateTime = new Date(`${formData.date}T${formData.startTime}`);
    const endDateTime = new Date(`${formData.date}T${formData.endTime}`);

    // Organizes data into form backend expects for calendar set event
    const payload = {
      summary: formData.title,
      start_time: startDateTime.toISOString(),
      end_time: endDateTime.toISOString(),
      location: formData.location || "",
      description: formData.description || "",
    };

    try {
      // Use api to send calendar event data to backend
      await api.post(
        "/api/v1/workouts/google-calendar/create-event/",
        payload,
      );
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

  // Fetch Google Calendar connection status after user is loaded
  useEffect(() => {
    if (loading || !user) return;

    const fetchStatus = async () => {
      try {
        const res = await api.get("/api/v1/workouts/google-calendar/status/", {
          headers: { "Cache-Control": "no-cache" },
        });
        setGoogleCalendarConnected(res.data.connected); // Update state so it can be displayed on screen
      } catch (err) {
        console.error("Failed to fetch Google Calendar status:", err);
        setGoogleCalendarConnected(false); // Default/fallback not connected
      }
    };

    fetchStatus();
  }, [loading, user]);

  // Fetch user profile once user is loaded
  useEffect(() => {
    if (loading || !user) return;

    api
      // Use api to get user profile data
      .get("/api/v1/users/profile/", {
        headers: { "Cache-Control": "no-cache" },
      })
      .then((res) => setProfile(res.data)) // Store user profile data in state
      .catch(() => setError("Failed to load profile."));
  }, [loading, user]);

  if (loading) return <Loading message="Checking authentication..." fullscreen={true} />;
  if (!user) return null;
  if (error) return <p className="text-red-500">{error}</p>;
  if (!profile) return <Loading message="Loading profile..." fullscreen={false} />;

  return (
    <div className="bg-slate-900 min-h-screen flex flex-col items-start px-6 py-12 pt-5">
      <div className="flex flex-col md:flex-row justify-center items-start gap-10 w-full max-w-7xl mx-auto">
      {/* Workout Scheduler Form */}
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-lg shadow-md max-w-md w-full flex-1 p-6 space-y-5"
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

      {/* User Profile & Password */}
      <aside className="bg-white rounded-lg shadow-md max-w-md w-full flex-1 p-8 flex flex-col items-center space-y-6">
        <h2 className="text-2xl font-bold text-slate-800 text-center w-full border-b border-gray-300 pb-3">
          User Profile
        </h2>

        {!googleCalendarConnected ? (
          <button
            onClick={() =>
              (window.location.href = `${
                import.meta.env.VITE_BACKEND_URL
              }/api/v1/workouts/google-calendar/auth-start/`)
            }
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

        {/* Profile Info */}
        <div className="w-full space-y-4 text-slate-700">
          <p>
            <span className="font-semibold">Username:</span> {profile.username}
          </p>
          <p>
            <span className="font-semibold">Email:</span> {profile.email}
          </p>
        </div>

        {/* Change Password Form */}
        <ChangePasswordForm />
      </aside>
      </div>
    </div>
  );
}
