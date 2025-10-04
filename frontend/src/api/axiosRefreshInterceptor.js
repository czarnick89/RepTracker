/**
 * Axios instance with automatic JWT refresh handling.
 *
 * - Creates a preconfigured `api` instance with baseURL from `.env` and cookies enabled.
 * - Adds a global response interceptor that:
 *    1. Allows normal responses to pass through.
 *    2. On 401 errors (unauthorized), attempts a token refresh unless:
 *       - The request was already a refresh/logout call.
 *       - The request has already been retried once.
 *    3. Handles multiple concurrent 401s by queueing failed requests until refresh completes.
 *    4. If refresh succeeds, replays failed requests with the new token.
 *    5. If refresh fails (especially with another 401), logs the user out.
 *
 * Key variables:
 * - `isRefreshing` → tracks whether a token refresh request is in progress.
 * - `failedQueue` → holds promises for requests waiting for refresh to complete.
 *
 * Logout behavior:
 * - Uses `performLogout` utility to run the app's logout flow (which calls the
 *   backend logout endpoint using a raw axios request) and then navigates the
 *   browser to the login page (`/login`).
 */

import axios from "axios";
import { performLogout } from "../utils/logout";

function interceptorLogout() {
  // Called when refresh fails and the interceptor decides to force logout.
  // Mark that the interceptor forced a logout so the AuthContext can avoid
  // immediately trying to refresh again and causing a redirect loop.
  try {
    sessionStorage.setItem("auth:interceptor_logout", Date.now().toString());
  } catch (e) {
    /* ignore sessionStorage errors */
  }

  // Try to run the standard logout flow so the backend invalidates the session
  // (performLogout uses raw axios so it won't be intercepted). If that fails,
  // fall back to a hard redirect.
  try {
    performLogout(null, (path) => {
      try {
        window.location.href = path || "/login";
      } catch (_) {
        /* ignore */
      }
    });
  } catch (e) {
    try {
      window.location.href = "/login";
    } catch (_) {
      /* ignore */
    }
  }
}

const api = axios.create({
  baseURL: `${import.meta.env.VITE_BACKEND_URL}`,
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  // Resolves or rejects all API requests that were queued while a token refresh was in progress.
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });

  failedQueue = [];
};

/**
 * Axios Response Interceptor
 *
 * Handles API responses and automatically refreshes JWT access tokens when expired.
 *
 * Flow:
 * 1. Successful responses: returned as-is.
 * 2. 401 Unauthorized responses:
 *    - If the request was already retried, logout the user.
 *    - If a token refresh is already in progress, queue this request to retry after refresh.
 *    - If no refresh in progress, attempt to refresh the access token:
 *        • On success: retry original request and resolve queued requests.
 *        • On failure (401): logout user and reject queued requests.
 * 3. Non-401 errors: rejected immediately.
 *
 * Notes:
 * - `isRefreshing` ensures only one refresh request happens at a time.
 * - `failedQueue` stores requests that hit 401 during a refresh and retries them afterward.
 * - `originalRequest._retry` prevents infinite retry loops.
 */
api.interceptors.response.use(
  // Success handler: just return the response as-is
  (response) => {
    return response; // No modifications needed for successful responses
  },
  // Error handler: handles failed responses (like 401 Unauthorized)
  async (error) => {
    const originalRequest = error.config; // Store the request that caused the error

    // Guard: if there's no original request/config (network errors, etc.), just reject
    if (!originalRequest || !originalRequest.url) {
      return Promise.reject(error);
    }

    // If the failed request is a refresh token or logout call, reject immediately
    if (
      originalRequest.url.includes("/token/refresh/") ||
      originalRequest.url.includes("/logout/")
    ) {
      return Promise.reject(error); // Don't try to refresh if these endpoints fail
    }

    // Check if the error status is 401 (Unauthorized)
    if (error.response?.status === 401) {

      // If we've already retried this request, logout user
      if (originalRequest._retry) {
        interceptorLogout(); // Clear auth and redirect to logout
        return Promise.reject(error); // Stop processing
      }

      // If a token refresh is already in progress, queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject }); // Add request to queue
        })
          .then(() => api(originalRequest)) // Retry original request after refresh completes
          .catch((err) => Promise.reject(err)); // Reject if refresh fails
      }

      // Start token refresh process
      originalRequest._retry = true; // Mark request as retried
      isRefreshing = true; // Indicate a refresh is in progress

      try {
  // Attempt to refresh the token using a raw axios call (bypass this interceptor)
  await axios.post(`${import.meta.env.VITE_BACKEND_URL}/api/v1/users/token/refresh/`, {}, { withCredentials: true });

        processQueue(null); // Resolve any queued requests with new token
        return api(originalRequest); // Retry the original request now
      } catch (refreshError) {
        processQueue(refreshError, null); // Reject queued requests if refresh fails

        // If refresh returned 401, logout user
        if (refreshError.response?.status === 401) {
          interceptorLogout();
        }

        return Promise.reject(refreshError); // Reject this failed request
      } finally {
        isRefreshing = false; // Reset refreshing flag
      }
    }

    // For all other errors (non-401), just reject
    return Promise.reject(error);
  }
);


export default api;
