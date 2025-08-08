import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useState, useEffect } from "react";
import Accordion from "../components/Accordion";
import axios from "axios";
import ExerciseCard from "../components/ExerciseCard";
import ConfirmModal from "../components/ConfirmModal";

export default function Dashboard() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [logoutModalOpen, setLogoutModalOpen] = useState(false);
  const [exercisesByWorkout, setExercisesByWorkout] = useState({});
  const [tempExerciseId, setTempExerciseId] = useState(-1);

  const handleLogout = () => {
    navigate("/logout");
  };

  const handleToggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleCloseSidebar = () => {
    setSidebarOpen(false);
  };

  useEffect(() => {
    axios
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

  const handleAddNewExercise = (workoutId) => {
    setExercisesByWorkout((prev) => {
      const prevExercises = prev[workoutId] || [];
      const blankExercise = { id: tempExerciseId, name: "", sets: [] };
      setTempExerciseId((id) => id - 1);
      return {
        ...prev,
        [workoutId]: [...prevExercises, blankExercise],
      };
    });
  };

  const handleSaveNewExercise = async (workoutId, tempId, newName) => {
    try {
      const res = await axios.post(
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
            to="/settings"
            onClick={handleCloseSidebar}
            className="hover:text-gray-300"
          >
            Settings
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

      {/* Main Content */}
      <main className="p-10 text-center">
        <button
          onClick={() => (window.location.href = "/workouts/new")}
          className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 transition mb-10"
        >
          Create New Workout
        </button>

        {loading ? (
          <p className="mt-8">Loading workouts...</p>
        ) : workouts.length === 0 ? (
          <p className="mt-8">You have no recent workouts.</p>
        ) : (
          workouts.map((workout) => (
            <Accordion
              key={workout.id}
              title={`${workout.name} - ${new Date(
                workout.date
              ).toLocaleDateString()}`}
            >
              <div className="flex flex-wrap justify-start">
                {(exercisesByWorkout[workout.id] || []).map((exercise) => (
                  <ExerciseCard
                    key={exercise.id}
                    exercise={exercise}
                    onExerciseNameSave={(newName) =>
                      handleSaveNewExercise(workout.id, exercise.id, newName)
                    }
                  />
                ))}
              </div>

              <button
                onClick={() => handleAddNewExercise(workout.id)}
                className="mt-4 bg-green-600 hover:bg-green-700 text-white rounded px-4 py-2"
              >
                Create New Exercise
              </button>
            </Accordion>
          ))
        )}
      </main>
    </div>
  );
}
