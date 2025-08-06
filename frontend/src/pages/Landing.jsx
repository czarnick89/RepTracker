export default function LandingPage() {
  return (
    <div className="p-10 text-center">
      <h1 className="text-4xl font-bold mb-4">Welcome to RepTrack</h1>
      <p className="text-lg text-gray-600 mb-6">
        Track your workouts, monitor progress, and stay consistent.
      </p>
      <a
        href="/login"
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
      >
        Log In
      </a>
    </div>
  );
}
