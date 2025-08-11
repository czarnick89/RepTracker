import api from '../api/axiosRefreshInterceptor';

export async function performLogout(setUserCallback, navigateCallback) {
  try {
    await api.post('/api/v1/users/logout/');
  } catch (err) {
    if (err.response?.status !== 401) {
      console.error("Logout error:", err);
    } // else ignore 401 on logout as “already logged out”
  }
  if (setUserCallback) setUserCallback(null);
  if (navigateCallback) navigateCallback('/login');
}


