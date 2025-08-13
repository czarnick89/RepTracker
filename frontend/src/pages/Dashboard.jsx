import { useState, useEffect } from "react";
import Accordion from "../components/Accordion";
import api from "../api/axiosRefreshInterceptor";
import ExerciseCard from "../components/ExerciseCard";
import ConfirmModal from "../components/ConfirmModal";
import WorkoutTitle from "../components/WorkoutTitle";

export default function Dashboard() {
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [exercisesByWorkout, setExercisesByWorkout] = useState({});
  const [tempExerciseId, setTempExerciseId] = useState(-1);
  const [newWorkout, setNewWorkout] = useState(null);
  const [tempWorkoutId, setTempWorkoutId] = useState(-1);
  const [workoutToDelete, setWorkoutToDelete] = useState(null);
  const [exerciseToDelete, setExerciseToDelete] = useState(null);
  const [showDeleteButtons, setShowDeleteButtons] = useState(false);

  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true); // tracks if there are more workouts to load
  const PAGE_SIZE = 10; // same as backend default limit

  useEffect(() => {
    fetchWorkouts(true); // reset on first load
  }, []);

  const fetchWorkouts = async (reset = false) => {
    try {
      const res = await api.get(
        "https://127.0.0.1:8000/api/v1/workouts/workouts/recent/",
        {
          withCredentials: true,
          params: {
            offset: reset ? 0 : offset,
            limit: PAGE_SIZE,
          },
        }
      );

      const sorted = [...res.data].sort(
        (a, b) => new Date(b.date) - new Date(a.date)
      );

      if (reset) {
        setWorkouts(sorted);
        const exercisesMap = {};
        sorted.forEach((w) => {
          exercisesMap[w.id] = w.exercises || [];
        });
        setExercisesByWorkout(exercisesMap);
        setOffset(sorted.length);
      } else {
        setWorkouts((prev) => [...prev, ...sorted]);
        setOffset((prev) => prev + sorted.length);

        // update exercises map
        setExercisesByWorkout((prev) => {
          const newMap = { ...prev };
          sorted.forEach((w) => {
            newMap[w.id] = w.exercises || [];
          });
          return newMap;
        });
      }

      // If we got fewer than PAGE_SIZE, there’s no more to load
      if (res.data.length < PAGE_SIZE) setHasMore(false);
    } catch (err) {
      console.error("Failed to load workouts", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddNewExercise = (workoutId) => {
    setExercisesByWorkout((prev) => {
      const prevExercises = prev[workoutId] || [];
      const blankExercise = {
        id: tempExerciseId,
        name: "",
        sets: [],
        workoutId,
      };
      setTempExerciseId((id) => id - 1);
      return {
        ...prev,
        [workoutId]: [...prevExercises, blankExercise],
      };
    });
  };

  const handleSaveNewExercise = async (workoutId, tempId, newName) => {
    try {
      const res = await api.post(
        "https://127.0.0.1:8000/api/v1/workouts/exercises/",
        { workout: workoutId, name: newName },
        { withCredentials: true }
      );
      setExercisesByWorkout((prev) => {
        const updatedExercises = prev[workoutId].map((ex) =>
          ex.id === tempId ? res.data : ex
        );
        return { ...prev, [workoutId]: updatedExercises };
      });
    } catch (error) {
      console.error("Failed to create new exercise", error);
    }
  };

  const handleExerciseNameSave = async (exercise, newName) => {
    if (exercise.id < 0) {
      await handleSaveNewExercise(exercise.workoutId, exercise.id, newName);
    } else {
      try {
        await api.patch(`/api/v1/workouts/exercises/${exercise.id}/`, {
          name: newName,
          workout: exercise.workoutId,
        });
      } catch (error) {
        console.error("Failed to update exercise name", error);
      }
    }
  };

  const handleDeleteExercise = async () => {
    if (!exerciseToDelete) return;
    const { workoutId, exerciseId } = exerciseToDelete;
    try {
      await api.delete(`/api/v1/workouts/exercises/${exerciseId}/`);
      setExercisesByWorkout((prev) => {
        const updated = { ...prev };
        updated[workoutId] = updated[workoutId].filter(
          (e) => e.id !== exerciseId
        );
        return updated;
      });
      setExerciseToDelete(null);
    } catch (error) {
      console.error("Failed to delete exercise:", error);
    }
  };

  const handleNewWorkoutNameBlur = async () => {
    if (!newWorkout || newWorkout.name.trim() === "") return;
    try {
      const res = await api.post(
        "/api/v1/workouts/workouts/",
        {
          name: newWorkout.name,
          date: newWorkout.date,
        },
        { withCredentials: true }
      );
      setWorkouts((prev) => [res.data, ...prev]);
      setExercisesByWorkout((prev) => ({
        ...prev,
        [res.data.id]: [],
      }));
      setNewWorkout(null);
      setTempWorkoutId((id) => id - 1);
    } catch (error) {
      console.error("Failed to create workout", error);
    }
  };

  const handleWorkoutNameUpdate = async (workoutId, newName) => {
    try {
      const res = await api.patch(`/api/v1/workouts/workouts/${workoutId}/`, {
        name: newName,
      });
      setWorkouts((prev) =>
        prev.map((w) =>
          w.id === workoutId ? { ...w, name: res.data.name } : w
        )
      );
    } catch (error) {
      console.error("Failed to update workout name", error);
    }
  };

  const handleDeleteWorkout = async () => {
    if (!workoutToDelete) return;
    try {
      await api.delete(`/api/v1/workouts/workouts/${workoutToDelete}/`);
      setWorkouts((prev) => prev.filter((w) => w.id !== workoutToDelete));
      setExercisesByWorkout((prev) => {
        const updated = { ...prev };
        delete updated[workoutToDelete];
        return updated;
      });
      setWorkoutToDelete(null);
    } catch (error) {
      console.error("Failed to delete workout:", error);
    }
  };

  if (loading) return <p>Loading workouts...</p>;

  return (
    <>
      <ConfirmModal
        isOpen={workoutToDelete !== null}
        title="Confirm Delete Workout"
        message="Are you sure you want to delete this workout?"
        onConfirm={handleDeleteWorkout}
        onCancel={() => setWorkoutToDelete(null)}
      />
      <ConfirmModal
        isOpen={exerciseToDelete !== null}
        title="Confirm Delete Exercise"
        message="Are you sure you want to delete this exercise?"
        onConfirm={handleDeleteExercise}
        onCancel={() => setExerciseToDelete(null)}
      />

      <div className="flex items-center justify-center mb-5 px-5 max-w-xl mx-auto relative">
        <button
          onClick={() =>
            setNewWorkout({
              id: tempWorkoutId,
              name: "",
              date: new Date().toISOString().slice(0, 10),
            })
          }
          className="bg-green-600 text-white px-8 py-3 rounded-md hover:bg-green-700 transition font-semibold"
        >
          New Workout
        </button>

        <button
          onClick={() => setShowDeleteButtons((show) => !show)}
          className="bg-red-600 text-white px-2 py-3 rounded-md hover:bg-red-700 transition font-semibold absolute right-5"
        >
          🗑️
        </button>
      </div>

      {newWorkout && (
        <Accordion
          key={newWorkout.id}
          title={
            <input
              type="text"
              autoFocus
              value={newWorkout.name}
              onChange={(e) =>
                setNewWorkout({ ...newWorkout, name: e.target.value })
              }
              onBlur={handleNewWorkoutNameBlur}
              className="bg-gray-700 text-white font-semibold rounded px-2 py-1 w-full"
              placeholder="Enter workout name"
            />
          }
        >
          <div className="p-4 text-gray-400">
            Add exercises after creating workout.
          </div>
        </Accordion>
      )}

      {workouts.length === 0 ? (
        <p>You have no recent workouts.</p>
      ) : (
        workouts.map((workout) => (
          <Accordion
            key={workout.id}
            title={
              <WorkoutTitle
                workout={workout}
                onNameUpdate={handleWorkoutNameUpdate}
                onDelete={() => setWorkoutToDelete(workout.id)}
                showDeleteButton={showDeleteButtons}
              />
            }
          >
            <div className="flex flex-wrap justify-start">
              {(exercisesByWorkout[workout.id] || []).map((exercise) => (
                <ExerciseCard
                  key={exercise.id}
                  exercise={exercise}
                  onExerciseNameSave={handleExerciseNameSave}
                  onDelete={() =>
                    setExerciseToDelete({
                      workoutId: workout.id,
                      exerciseId: exercise.id,
                    })
                  }
                  showDeleteButton={showDeleteButtons}
                />
              ))}
            </div>
            <div className="flex justify-center mt-4">
              <button
                onClick={() => handleAddNewExercise(workout.id)}
                className="mt-4 bg-blue-600 hover:bg-blue-700 text-white rounded px-4 py-2"
              >
                New Exercise
              </button>
            </div>
          </Accordion>
        ))
      )}
      {hasMore && (
        <div className="flex justify-center mt-4">
          <button
            onClick={() => fetchWorkouts()}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
          >
            Load More Workouts
          </button>
        </div>
      )}
    </>
  );
}
