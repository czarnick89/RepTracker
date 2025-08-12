import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useState, useEffect } from "react";
import Accordion from "../components/Accordion";
import api from "../api/axiosRefreshInterceptor";
import ExerciseCard from "../components/ExerciseCard";
import ConfirmModal from "../components/ConfirmModal";
import WorkoutTitle from "../components/WorkoutTitle";

export default function Dashboard() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [logoutModalOpen, setLogoutModalOpen] = useState(false);
  const [exercisesByWorkout, setExercisesByWorkout] = useState({});
  const [tempExerciseId, setTempExerciseId] = useState(-1);
  const [newWorkout, setNewWorkout] = useState(null);
  const [tempWorkoutId, setTempWorkoutId] = useState(-1);
  const [workoutToDelete, setWorkoutToDelete] = useState(null);
  const [exerciseToDelete, setExerciseToDelete] = useState(null);
  const [showDeleteButtons, setShowDeleteButtons] = useState(false);

  useEffect(() => {
    api
      .get("https://127.0.0.1:8000/api/v1/workouts/workouts/recent/", {
        withCredentials: true,
      })
      .then((res) => {
        // Sort newest first
        const sorted = [...res.data].sort(
          (a, b) => new Date(b.date) - new Date(a.date)
        );
        setWorkouts(sorted);

        // Initialize exercisesByWorkout state: map workout.id -> exercises array
        const exercisesMap = {};
        sorted.forEach((w) => {
          exercisesMap[w.id] = w.exercises || [];
        });
        setExercisesByWorkout(exercisesMap);
      })
      .catch((err) => {
        console.error("Failed to load workouts", err);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleLogout = () => {
    navigate("/logout");
  };

  const handleToggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleCloseSidebar = () => {
    setSidebarOpen(false);
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

      const createdExercise = res.data;

      setExercisesByWorkout((prev) => {
        const updatedExercises = prev[workoutId].map((ex) =>
          ex.id === tempId ? createdExercise : ex
        );
        return { ...prev, [workoutId]: updatedExercises };
      });
    } catch (error) {
      console.error("Failed to create new exercise", error);
    }
  };

  const handleExerciseNameSave = async (exercise, newName) => {
    if (exercise.id < 0) {
      // Creating new exercise
      await handleSaveNewExercise(exercise.workoutId, exercise.id, newName);
    } else {
      // Updating existing exercise
      try {
        const res = await api.patch(
          `/api/v1/workouts/exercises/${exercise.id}/`,
          {
            name: newName, // String, NOT an object
            workout: exercise.workoutId, // include workout id as number
          },
          { withCredentials: true }
        );

        const updatedExercise = res.data;

        // update local state, etc.
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

  const handleConfirmDeleteExercise = (workoutId, exerciseId) => {
    setExerciseToDelete({ workoutId, exerciseId });
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

  const handleConfirmDeleteWorkout = (workoutId) => {
    setWorkoutToDelete(workoutId);
  };

  if (loading) return <p>Loading workouts...</p>;

  return (
    <div className="relative min-h-screen bg-blue-900 text-white">
      {/* Navbar */}
      <nav className="bg-gray-800 text-white p-4 flex items-center justify-center relative">
        <button
          onClick={handleToggleSidebar}
          className="text-white text-2xl focus:outline-none absolute left-4"
          aria-label="Toggle Menu"
        >
          &#9776;
        </button>

        <Link
          to="/dashboard"
          className="text-xl font-bold hover:text-gray-300"
          onClick={handleCloseSidebar}
        >
          RepTrack Dashboard
        </Link>
      </nav>

      {/* Sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-gray-900/50 z-40"
          onClick={handleCloseSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full bg-gray-900 text-white z-50 transform transition-transform duration-300 ease-in-out
      ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
    `}
        style={{ width: "50vw", maxWidth: "300px" }}
      >
        <div className="p-6 flex flex-col space-y-6">
          <Link
            to="/dashboard"
            onClick={handleCloseSidebar}
            className="hover:text-gray-300"
          >
            Dashboard
          </Link>
          <Link
            to="/dashboard"
            onClick={handleCloseSidebar}
            className="hover:text-gray-300"
          >
            Analytics
          </Link>
          <Link
            to="/profile"
            onClick={handleCloseSidebar}
            className="hover:text-gray-300"
          >
            Profile
          </Link>
          <button
            onClick={() => setLogoutModalOpen(true)}
            className="text-red-600 border border-red-600 hover:bg-red-600 hover:text-white transition px-3 py-1 rounded text-center"
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Confirm Logout Modal */}
      <ConfirmModal
        isOpen={logoutModalOpen}
        title="Confirm Logout"
        message="Are you sure you want to log out?"
        onConfirm={() => {
          setLogoutModalOpen(false);
          setSidebarOpen(false);
          handleLogout();
        }}
        onCancel={() => setLogoutModalOpen(false)}
      />

      {/* Confirm Delete Workout Modal */}
      <ConfirmModal
        isOpen={workoutToDelete !== null}
        title="Confirm Delete Workout"
        message="Are you sure you want to delete this workout? This action cannot be undone."
        onConfirm={handleDeleteWorkout}
        onCancel={() => setWorkoutToDelete(null)}
      />

      {/* Confirm Delete Exercise Modal */}
      <ConfirmModal
        isOpen={exerciseToDelete !== null}
        title="Confirm Delete Exercise"
        message="Are you sure you want to delete this exercise? This action cannot be undone."
        onConfirm={handleDeleteExercise}
        onCancel={() => setExerciseToDelete(null)}
      />

      {/* Main Content */}
      <main className="p-5 text-center">
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

        {loading ? (
          <p className="mt-8">Loading workouts...</p>
        ) : (
          <>
            {/* New workout inline accordion with input title */}
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

            {/* Existing workouts */}
            {workouts.length === 0 ? (
              <p className="mt-8">You have no recent workouts.</p>
            ) : (
              workouts.map((workout) => (
                <Accordion
                  key={workout.id}
                  title={
                    <WorkoutTitle
                      workout={workout}
                      onNameUpdate={handleWorkoutNameUpdate}
                      onDelete={() => handleConfirmDeleteWorkout(workout.id)}
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
                          handleConfirmDeleteExercise(workout.id, exercise.id)
                        }
                        showDeleteButton={showDeleteButtons}
                      />
                    ))}
                  </div>

                  <button
                    onClick={() => handleAddNewExercise(workout.id)}
                    className="mt-4 bg-blue-600 hover:bg-blue-700 text-white rounded px-4 py-2"
                  >
                    New Exercise
                  </button>
                </Accordion>
              ))
            )}
          </>
        )}
      </main>
    </div>
  );
}
