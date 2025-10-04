import axios from 'axios';

// Performs user logout by calling backend API and updating frontend state/navigation
export async function performLogout(setUserCallback, navigateCallback) {
  try {
    // Call the backend logout endpoint (invalidates tokens).
    // Use a plain axios request here (not the intercepted `api`) to avoid
    // triggering the refresh-interceptor during logout and creating a
    // redirect loop.
    await axios.post(`${import.meta.env.VITE_BACKEND_URL}/api/v1/users/logout/`, {}, { withCredentials: true });
  } catch (err) {
    // Ignore 401 because user may not be logged
    if (err.response?.status !== 401) {
      console.error("Logout error:", err);
    } 
  }
  // Clear user state in frontend if callback is provided
  if (setUserCallback) setUserCallback(null);
  // Redirect to login page if callback is provided
  if (navigateCallback) navigateCallback('/login');
}


