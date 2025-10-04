// Reusable loading UI. If `fullscreen` is true it covers the viewport
// with the app blue background to match the rest of the UI. If false,
// it renders a compact inline loader suitable for modals or small areas.
export default function Loading({ message = "Loading...", fullscreen = true }) {
  if (fullscreen) {
    return (
      <div
        role="status"
        aria-live="polite"
        className="min-h-screen flex items-center justify-center bg-blue-600 text-white"
      >
        <div className="flex flex-col items-center gap-4">
          <svg
            className="animate-spin h-10 w-10 text-white"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
            ></path>
          </svg>
          <span className="text-lg font-medium">{message}</span>
        </div>
      </div>
    );
  }

  // Compact inline loader for modals / small areas
  return (
    <div role="status" aria-live="polite" className="flex items-center gap-2">
      <svg
        className="animate-spin h-5 w-5 text-blue-600"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        ></circle>
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
        ></path>
      </svg>
      <span className="text-sm text-gray-200">{message}</span>
    </div>
  );
}
