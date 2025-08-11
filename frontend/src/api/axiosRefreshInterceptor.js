import axios from "axios";
import { performLogout } from "../utils/logout";

function interceptorLogout() {
  // console.log("Refresh token invalid, logging out and redirecting...");
  performLogout(
    () => {},
    () => {
      window.location.href = "/logout";
    }
  );
}

const api = axios.create({
  baseURL: "https://127.0.0.1:8000/",
  withCredentials: true, // Important so cookies are sent
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
    // console.log(`[Interceptor] Response success: ${response.config.url}`);
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    // console.log(`[Interceptor] Response error: ${originalRequest.url}, status: ${error.response?.status}`);

    if (
      originalRequest.url.includes("/token/refresh/") ||
      originalRequest.url.includes("/logout/")
    ) {
      // console.log("[Interceptor] Rejecting error without retry (refresh/logout endpoint).");
      return Promise.reject(error);
    }

    if (error.response?.status === 401) {
      if (originalRequest._retry) {
        // console.log("[Interceptor] Already retried once, calling interceptorLogout.");
        interceptorLogout();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // console.log("[Interceptor] Refreshing token, queuing request.");
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
        // console.log("[Interceptor] Token refresh successful, retrying original request.");
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);

        if (refreshError.response?.status === 401) {
          // console.log("[Interceptor] Refresh token invalid, calling interceptorLogout.");
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
