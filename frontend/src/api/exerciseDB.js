
export const getExerciseByName = async (name) => {
  const res = await fetch(`https://127.0.0.1:8000/api/v1/workouts/exercise-by-name?name=${encodeURIComponent(name)}`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error("Failed to fetch exercise");
  return res.json();
};

export const getExerciseGifUrl = (exerciseId, resolution = 180) => {
  return `https://127.0.0.1:8000/api/v1/workouts/exercise-gif?exerciseId=${exerciseId}&resolution=${resolution}`;
};
