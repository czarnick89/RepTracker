import { useState } from "react";
import api from "../api/axiosRefreshInterceptor"; // <- use your custom api
import { performLogout } from "../utils/logout";

export default function ChangePasswordForm() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState(""); // consistent naming
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setStatus(null);

    if (newPassword !== confirmPassword) {
      setMessage("New passwords do not match.");
      setStatus("error");
      return;
    }

    try {
      const res = await api.post("/api/v1/users/change-password/", {
        old_password: oldPassword,
        new_password: newPassword,
      });

      setMessage(res.data.detail || "Password updated successfully.");
      setStatus("success");

      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      if (err.response?.status === 401) {
        performLogout(
          () => {},
          () => {
            window.location.href = "/logout";
          }
        );
      } else {
        const error =
          err.response?.data?.error?.[0] ||
          err.response?.data?.error ||
          "Failed to change password.";
        setMessage(Array.isArray(error) ? error.join(" ") : error);
        setStatus("error");
      }
    }
  };

  return (
    <div className="w-full mt-6 border-t border-gray-300 pt-4">
      <h3 className="text-xl font-semibold text-slate-800 mb-3">Change Password</h3>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <input
          type="password"
          placeholder="Current Password"
          value={oldPassword}
          onChange={(e) => setOldPassword(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 text-black"
          required
        />
        <input
          type="password"
          placeholder="New Password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 text-black"
          required
        />
        <input
          type="password"
          placeholder="Confirm New Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 text-black"
          required
        />
        <button
          type="submit"
          className="w-full bg-green-600 text-white font-semibold py-2 rounded-md hover:bg-green-700 transition shadow-md"
        >
          Change Password
        </button>
        {message && (
          <p
            className={`text-sm mt-1 ${
              status === "success" ? "text-green-600" : "text-red-600"
            }`}
          >
            {message}
          </p>
        )}
      </form>
    </div>
  );
}
