// Fetch exercise details from backend (proxy to exerciseDB) by name
export const getExerciseByName = async (name) => {
  const res = await fetch(
    `${import.meta.env.VITE_BACKEND_URL}/api/v1/workouts/exercise-by-name?name=${encodeURIComponent(name)}`,
    { credentials: 'include' }
  );
  // Handle throttling
  if (res.status === 429) {
    const retryAfter = res.headers.get("Retry-After");
    throw new Error(
      retryAfter
        ? `Limit reached. Try again in ${Math.ceil(retryAfter / 60)} minutes.`
        : "Daily limit reached. Try again later."
    );
  }

  if (!res.ok) throw new Error("Failed to fetch exercise");

  return res.json();
};

// Fetch exercise gif from backend (proxy to exerciseDB) by id
export const getExerciseGifUrl = (exerciseId, resolution = 180) => {
  return `${import.meta.env.VITE_BACKEND_URL}/api/v1/workouts/exercise-gif?exerciseId=${exerciseId}&resolution=${resolution}`;
};
