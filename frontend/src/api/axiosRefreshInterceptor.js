import axios from "axios";
import { performLogout } from "../utils/logout";

function interceptorLogout() {
  performLogout(
    () => {},
    () => {
      window.location.href = "/logout";
    }
  );
}

const api = axios.create({
  baseURL: `${import.meta.env.VITE_BACKEND_URL}`,
  withCredentials: true, 
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });

  failedQueue = [];
};

api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (
      originalRequest.url.includes("/token/refresh/") ||
      originalRequest.url.includes("/logout/")
    ) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401) {
      if (originalRequest._retry) {
        interceptorLogout();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => api(originalRequest))
          .catch((err) => Promise.reject(err));
      }

      console.log("[Interceptor] Starting token refresh.");
      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await api.post("/api/v1/users/token/refresh/");
        processQueue(null);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);

        if (refreshError.response?.status === 401) {
          interceptorLogout();
        }

        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
