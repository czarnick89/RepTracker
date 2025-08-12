const API_BASE = "https://exercisedb.p.rapidapi.com";
const API_KEY = import.meta.env.VITE_RAPIDAPI_KEY;

export const getExerciseByName = async (name) => {
  const res = await fetch(`${API_BASE}/exercises/name/${encodeURIComponent(name)}`, {
    headers: {
      "X-RapidAPI-Key": API_KEY,
      "X-RapidAPI-Host": "exercisedb.p.rapidapi.com",
    },
  });
  if (!res.ok) throw new Error("Failed to fetch exercise");
  return res.json();
};

export const getExerciseGifUrl = (exerciseId, resolution = 180) => {
  return `https://127.0.0.1:8000/api/v1/workouts/exercise-gif?exerciseId=${exerciseId}&resolution=${resolution}`;
};
