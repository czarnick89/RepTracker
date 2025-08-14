import api from '../api/axiosRefreshInterceptor';

// Performs user logout by calling backend API and updating frontend state/navigation
export async function performLogout(setUserCallback, navigateCallback) {
  try {
    // Call the backend logout endpoint (invalidates tokens)
    await api.post('/api/v1/users/logout/');
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


