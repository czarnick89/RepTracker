import { useState, useEffect } from "react";
import Accordion from "../components/Accordion";
import api from "../api/axiosRefreshInterceptor";
import ExerciseCard from "../components/ExerciseCard";
import ConfirmModal from "../components/ConfirmModal";
import WorkoutTitle from "../components/WorkoutTitle";
import Loading from "../components/Loading";

// Dashboard component: displays recent workouts, allows creating/editing/deleting workouts and exercises
export default function Dashboard() {
  // Workouts and exercises state
  const [workouts, setWorkouts] = useState([]); // list of workouts
  const [loading, setLoading] = useState(true); // loading indicator
  const [exercisesByWorkout, setExercisesByWorkout] = useState({}); // mapping of workoutId -> exercises

  // Temp IDs for client-side creation before backend returns actual IDs
  const [tempExerciseId, setTempExerciseId] = useState(-1);
  const [focusExerciseId, setFocusExerciseId] = useState(null);
  const [tempWorkoutId, setTempWorkoutId] = useState(-1);

  // State for new items and deletions
  const [newWorkout, setNewWorkout] = useState(null); // new workout being created
  const [workoutToDelete, setWorkoutToDelete] = useState(null); // ID of workout pending deletion
  const [exerciseToDelete, setExerciseToDelete] = useState(null); // object {workoutId, exerciseId}
  const [showDeleteButtons, setShowDeleteButtons] = useState(false); // toggle delete buttons for UX

  // Flash feedback state for save success/error
  const [flashState, setFlashState] = useState({}); // { [key]: 'success' | 'error' }

  // Pagination state
  const [offset, setOffset] = useState(0); // for API pagination
  const [hasMore, setHasMore] = useState(true); // track if more workouts are available
  const PAGE_SIZE = 10; // number of workouts per API call

  // Helper to trigger flash feedback on an element
  const triggerFlash = (key, status) => {
    setFlashState((prev) => ({ ...prev, [key]: status }));
    // Clear flash after animation completes
    setTimeout(() => {
      setFlashState((prev) => {
        const updated = { ...prev };
        delete updated[key];
        return updated;
      });
    }, 600);
  };

  // Fetch recent workouts on load
  useEffect(() => {
    fetchWorkouts(true);
  }, []);

  // Fetch workouts helper
  const fetchWorkouts = async (reset = false) => {
    try {
      // Use api to get recent workouts
      const res = await api.get(
        `${import.meta.env.VITE_BACKEND_URL}/api/v1/workouts/workouts/recent/`,
        {
          params: {
            offset: reset ? 0 : offset, // Helps keep track of how many additional we have loaded using Load More Workouts button
            limit: PAGE_SIZE, // How many workouts to fetch per Load More Workouts button press
          },
        }
      );
      // Sort workouts by date descending
      const sorted = [...res.data].sort(
        (a, b) => new Date(b.date) - new Date(a.date)
      );

      if (reset) {
        setWorkouts(sorted); // Replace sorted workouts in state
        const exercisesMap = {};
        // Map workout ID to exercise to generate exercise array. Needed so exercises are placed with proper workouts
        sorted.forEach((w) => {
          exercisesMap[w.id] = w.exercises || [];
        });
        setExercisesByWorkout(exercisesMap); // Save exercise array to state
        setOffset(sorted.length); // Update offset so next push of Load More Workouts button will load proper workouts
      } else {
        setWorkouts((prev) => [...prev, ...sorted]); // Append newly fetched workouts to workouts state
        setOffset((prev) => prev + sorted.length); // Update offset so next push of Load More Workouts button will load proper workouts

        // Update exercises map for newly fetched workouts
        setExercisesByWorkout((prev) => {
          const newMap = { ...prev }; // Start a new map with old map
          sorted.forEach((w) => {
            // Map workout ID to exercise to add to new map
            newMap[w.id] = w.exercises || [];
          });
          return newMap;
        });
      }

      // If we got fewer than PAGE_SIZE, there’s no more to load
      if (res.data.length < PAGE_SIZE) setHasMore(false); // when hasmore = false the Load More Workouts button is not rendered
    } catch (err) {
      console.error("Failed to load workouts", err);
    } finally {
      setLoading(false);
    }
  };

  // Function to add a new blank exercise to a workout
  const handleAddNewExercise = (workoutId) => {
    // Compute a temp id to use for this new exercise so we can focus it after render
    const tempId = tempExerciseId;
    // Decrement tempExerciseId for next new exercise
    setTempExerciseId((id) => id - 1);

    // Update the exercisesByWorkout state with the new blank exercise
    setExercisesByWorkout((prev) => {
      const prevExercises = prev[workoutId] || [];
      const blankExercise = { id: tempId, name: "", sets: [], workoutId };
      return { ...prev, [workoutId]: [...prevExercises, blankExercise] };
    });

    // Request that the newly-added exercise's name input receive focus
    setFocusExerciseId(tempId);
  };

  // Function to save a newly added exercise to the backend
  const handleSaveNewExercise = async (workoutId, tempId, newName) => {
    try {
      // 1. Send POST request to backend to create the new exercise
      //    - workoutId links the exercise to the correct workout
      //    - newName is the exercise name provided by user
      const res = await api.post(
        `${import.meta.env.VITE_BACKEND_URL}/api/v1/workouts/exercises/`,
        { workout: workoutId, name: newName }
      );
      // 2. Update frontend state after backend confirms creation
      setExercisesByWorkout((prev) => {
        // Map over existing exercises for this workout
        const updatedExercises = prev[workoutId].map((ex) =>
          // Replace the temporary exercise (tempId) with the saved one from backend (res.data)
          ex.id === tempId ? res.data : ex
        );
        // Return new state object
        return { ...prev, [workoutId]: updatedExercises };
      });
      // Return success for flash feedback
      return { success: true, exerciseId: tempId };
    } catch (error) {
      console.error("Failed to create new exercise", error);
      return { success: false, exerciseId: tempId };
    }
  };

  // Function to save or update an exercise name
  const handleExerciseNameSave = async (exercise, newName) => {
    if (exercise.id < 0) {
      // If exercise has a temporary negative ID, it's a new exercise
      // Call handleSaveNewExercise to create it on the backend
      const result = await handleSaveNewExercise(exercise.workoutId, exercise.id, newName);
      triggerFlash(`exercise-${exercise.id}`, result.success ? 'success' : 'error');
    } else {
      // If exercise already exists in backend, update its name via PATCH
      try {
        await api.patch(`/api/v1/workouts/exercises/${exercise.id}/`, {
          name: newName,
          workout: exercise.workoutId,
        });
        triggerFlash(`exercise-${exercise.id}`, 'success');
      } catch (error) {
        console.error("Failed to update exercise name", error);
        triggerFlash(`exercise-${exercise.id}`, 'error');
      }
    }
  };

  // Function to delete an exercise from a workout
  const handleDeleteExercise = async () => {
    // Exit early if no exercise is selected for deletion
    if (!exerciseToDelete) return;
    const { workoutId, exerciseId } = exerciseToDelete;
    
    // If exercise has a temporary negative ID, it hasn't been saved to backend yet
    // Just remove it from frontend state without making an API call
    if (exerciseId < 0) {
      setExercisesByWorkout((prev) => {
        const updated = { ...prev };
        // Filter out the unsaved exercise from its workout's array
        updated[workoutId] = updated[workoutId].filter(
          (e) => e.id !== exerciseId
        );
        return updated;
      });
      // Clear the temporary deletion state
      setExerciseToDelete(null);
      return;
    }
    
    // For exercises that exist on the backend, send DELETE request
    try {
      // Send DELETE request to backend to remove exercise
      await api.delete(`/api/v1/workouts/exercises/${exerciseId}/`);
      // Update frontend state to remove the exercise from the exercisesByWorkout map
      setExercisesByWorkout((prev) => {
        const updated = { ...prev };
        // Filter out the deleted exercise from its workout's array
        updated[workoutId] = updated[workoutId].filter(
          (e) => e.id !== exerciseId
        );
        return updated;
      });
      // Clear the temporary deletion state
      setExerciseToDelete(null);
    } catch (error) {
      console.error("Failed to delete exercise:", error);
    }
  };

  // Function to handle new workout name on blur
  const handleNewWorkoutNameBlur = async () => {
    // Guard clause: if no newWorkout is set, or its name is empty/whitespace, exit early
    if (!newWorkout || newWorkout.name.trim() === "") return;
    try {
      // Send POST request to backend to create a new workout
      const res = await api.post(
        "/api/v1/workouts/workouts/",
        {
          name: newWorkout.name,
          date: newWorkout.date,
        }
      );
      // Add the newly created workout to the top of the workouts state array
      setWorkouts((prev) => [res.data, ...prev]);
      // Initialize an empty exercises array for the new workout in the map
      setExercisesByWorkout((prev) => ({
        ...prev,
        [res.data.id]: [],
      }));
      // Clear the temporary newWorkout state
      setNewWorkout(null);
      // Decrement tempWorkoutId for the next new workout
      setTempWorkoutId((id) => id - 1);
    } catch (error) {
      console.error("Failed to create workout", error);
    }
  };

    // Function to update a workouts name
  const handleWorkoutNameUpdate = async (workoutId, newName) => {
    try {
      // Send PATCH request to backend to update the workout's name
      const res = await api.patch(`/api/v1/workouts/workouts/${workoutId}/`, {
        name: newName,
      });
      // Update the local state to reflect the new name without refetching all workouts
      setWorkouts((prev) =>
        prev.map((w) =>
          w.id === workoutId ? { ...w, name: res.data.name } // Replace the name for the updated workout
      : w // Leave other workouts unchanged
        )
      );
      triggerFlash(`workout-${workoutId}`, 'success');
    } catch (error) {
      console.error("Failed to update workout name", error);
      triggerFlash(`workout-${workoutId}`, 'error');
    }
  };

  // Function to handle deleting workouts
  const handleDeleteWorkout = async () => {
    // Guard clause: exit early if no workout is selected for deletion
    if (!workoutToDelete) return;
    
    // If workout has a temporary negative ID, it hasn't been saved to backend yet
    // Just remove it from frontend state without making an API call
    if (workoutToDelete < 0) {
      setWorkouts((prev) => prev.filter((w) => w.id !== workoutToDelete));
      setExercisesByWorkout((prev) => {
        const updated = { ...prev };
        delete updated[workoutToDelete];
        return updated;
      });
      setWorkoutToDelete(null);
      return;
    }
    
    // For workouts that exist on the backend, send DELETE request
    try {
      // Send DELETE request to backend to remove the workout
      await api.delete(`/api/v1/workouts/workouts/${workoutToDelete}/`);
      // Update local workouts state to remove the deleted workout
      setWorkouts((prev) => prev.filter((w) => w.id !== workoutToDelete));
      // Update exercisesByWorkout state to remove any exercises associated with the deleted workout
      setExercisesByWorkout((prev) => {
        const updated = { ...prev };
        delete updated[workoutToDelete];
        return updated;
      });
      // Clear the temporary state for the workout-to-delete
      setWorkoutToDelete(null);
    } catch (error) {
      console.error("Failed to delete workout:", error);
    }
  };

  // Function to handle the weight change preference option on exercises
  const handleWeightPreferenceChange = async (
    workoutId,
    exerciseId,
    newPreference
  ) => {
    try {
      // Send request to backend first, wait for confirmation
      const res = await api.patch(
        `/api/v1/workouts/exercises/${exerciseId}/`,
        { weight_change_preference: newPreference }
      );

      // Only update local state after backend confirms success
      setExercisesByWorkout((prev) => {
        const updatedExercises = prev[workoutId].map((ex) =>
          ex.id === exerciseId
            ? { ...ex, weight_change_preference: res.data.weight_change_preference }
            : ex
        );
        return { ...prev, [workoutId]: updatedExercises };
      });
      triggerFlash(`exercise-${exerciseId}`, 'success');
    } catch (err) {
      console.error("Failed to update weight preference:", err);
      triggerFlash(`exercise-${exerciseId}`, 'error');
    }
  };

  if (loading) return <Loading message="Loading workouts..." fullscreen={true} />;

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

      <div className="sticky top-[56px] z-20 bg-blue-900 py-3 -mx-5 px-5 mb-5">
        <div className="flex items-center justify-center max-w-xl mx-auto relative">
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
      </div>

      {newWorkout && (
        <Accordion
          key={newWorkout.id}
          title={
            <div className="flex items-center justify-between">
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
              {showDeleteButtons && (
                <button
                  onClick={() => setNewWorkout(null)}
                  className="ml-2 text-red-600 hover:text-red-800 font-bold"
                  title="Delete workout"
                  aria-label="Delete new workout"
                >
                  🗑️
                </button>
              )}
            </div>
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
                flashStatus={flashState[`workout-${workout.id}`]}
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
                  onWeightPreferenceChange={(exerciseId, newPreference) =>
                    handleWeightPreferenceChange(
                      workout.id,
                      exerciseId,
                      newPreference
                    )
                  }
                  autoFocus={exercise.id === focusExerciseId}
                  onAutoFocusComplete={() => setFocusExerciseId(null)}
                  flashStatus={flashState[`exercise-${exercise.id}`]}
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
