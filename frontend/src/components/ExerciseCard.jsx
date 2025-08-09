import React, { useState, useRef } from "react";
// import axios from "axios";
import api from "../api/axiosRefreshInterceptor";

export default function ExerciseCard({
  exercise,
  onExerciseNameSave,
  onDelete,
  showDeleteButton,
}) {
  const [exerciseName, setExerciseName] = useState(exercise.name);
  // For sets, keep track of reps and weight locally too:
  const [sets, setSets] = useState(exercise.sets);
  // Track which set is new and pending save
  const [newSetId, setNewSetId] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [setToDelete, setSetToDelete] = useState(null);

  const weightInputRef = useRef(null);

  // Add a useEffect to sync local exerciseName when exercise prop changes (e.g., after saving new exercise)
  React.useEffect(() => {
    setExerciseName(exercise.name);
    setSets(exercise.sets);
  }, [exercise]);

  // PATCH update exercise name on blur
  const updateExerciseName = () => {
    if (exerciseName === exercise.name) return;

    if (exercise.id < 0) {
      // Call parent's callback to create exercise on backend
      if (onExerciseNameSave) {
        onExerciseNameSave(exerciseName);
      }
      return;
    }

    // Existing PATCH logic for existing exercises
    api
      .patch(
        `https://127.0.0.1:8000/api/v1/workouts/exercises/${exercise.id}/`,
        { name: exerciseName },
        { withCredentials: true }
      )
      .catch((err) => console.error("Failed to update exercise name", err));
  };

  // PATCH update set on blur
  const updateSet = (setId, newReps, newWeight) => {
    if (setId < 0) return; // don't PATCH sets that haven't been created yet

    api
      .patch(
        `https://127.0.0.1:8000/api/v1/workouts/sets/${setId}/`,
        { reps: Number(newReps), weight: normalizeWeight(newWeight) },
        { withCredentials: true }
      )
      .catch((err) => console.error("Failed to update set", err));
  };

  // POST create new set in backend
  const createNewSet = (reps, weight) => {
    return api
      .post(
        `https://127.0.0.1:8000/api/v1/workouts/sets/`,
        {
          exercise: exercise.id,
          reps: Number(reps),
          weight: normalizeWeight(weight),
        },
        { withCredentials: true }
      )
      .then((res) => res.data)
      .catch((err) => {
        console.error("Failed to create new set", err);
        throw err;
      });
  };

  const deleteSet = (setId) => {
    if (setId < 0) {
      // Remove locally
      setSets((prev) => prev.filter((s) => s.id !== setId));
      if (newSetId === setId) setNewSetId(null);
      return;
    }

    api
      .delete(`https://127.0.0.1:8000/api/v1/workouts/sets/${setId}/`, {
        withCredentials: true,
      })
      .then(() => {
        setSets((prev) => prev.filter((s) => s.id !== setId));
      })
      .catch((err) => console.error("Failed to delete set", err));
  };

  // Handle reps or weight change locally
  const handleSetChange = (setId, field, value) => {
    setSets((prev) =>
      prev.map((s) => (s.id === setId ? { ...s, [field]: value } : s))
    );
  };

  const handleAddNewSet = () => {
    // Create a temp set id for local tracking (negative to avoid clashing)
    const tempId = Math.min(...sets.map((s) => s.id), 0) - 1;
    const blankSet = { id: tempId, reps: "", weight: "" };
    setSets((prev) => [...prev, blankSet]);
    setNewSetId(tempId);

    // Focus weight input on next tick
    setTimeout(() => {
      if (weightInputRef.current) weightInputRef.current.focus();
    }, 100);
  };

  // Validation helpers
  const isValidReps = (val) => {
    const num = Number(val);
    return Number.isInteger(num) && num > 0;
  };
  const isValidWeight = (val) => {
    const num = Number(val);
    return !isNaN(num) && num >= 0;
  };

  const formatNumber = (num) => {
    if (num == null) return "";
    // Convert to number first, then check if integer
    const n = Number(num);
    return Number.isInteger(n)
      ? n.toString()
      : n.toFixed(2).replace(/\.?0+$/, "");
  };

  // When reps or weight changes for new set, check if both valid and send create
  const handleNewSetBlur = (set) => {
    if (set.id === newSetId) {
      if (isValidReps(set.reps) && isValidWeight(set.weight)) {
        createNewSet(set.reps, set.weight)
          .then((createdSet) => {
            // Replace temp set with backend set (with proper id)
            setSets((prev) =>
              prev.map((s) => (s.id === newSetId ? createdSet : s))
            );
            setNewSetId(null);
          })
          .catch(() => {
            // On failure you can decide to remove new set or keep it for retry
          });
      }
    }
  };

  const normalizeWeight = (weight) => {
    if (weight === "" || weight === null || weight === undefined) return 0;
    return Number(weight);
  };

  return (
    <div className="bg-gray-800 rounded-md p-4 m-2 flex-grow min-w-[180px] max-w-[300px] border border-gray-600">
      {/* Editable exercise name */}
      <div className="flex items-center space-x-2 mb-4">
        <input
          type="text"
          value={exerciseName}
          onChange={(e) => setExerciseName(e.target.value)}
          onBlur={updateExerciseName}
          className="flex-grow bg-gray-700 text-white font-semibold text-center rounded px-2 py-1"
        />
        {showDeleteButton && (
          <button
            onClick={onDelete}
            className="text-red-600 hover:text-red-800 font-bold px-3 py-1 rounded"
            aria-label={`Delete exercise ${exerciseName}`}
            type="button"
          >
            🗑️
          </button>
        )}
      </div>

      <div className="flex flex-col items-center space-y-1 font-mono text-lg w-full">
        {sets.map((set) => (
          <div
            key={set.id}
            className="flex justify-center gap-2 border-b border-gray-600 pb-1 w-full"
          >
            {/* Editable reps */}
            <input
              type="number"
              className="w-10 text-center bg-gray-700 text-white rounded no-spin"
              value={formatNumber(set.reps)}
              onChange={(e) => handleSetChange(set.id, "reps", e.target.value)}
              onBlur={() => {
                if (set.id === newSetId) {
                  handleNewSetBlur(set);
                } else {
                  updateSet(
                    set.id,
                    sets.find((s) => s.id === set.id).reps,
                    set.weight
                  );
                }
              }}
            />

            <span>@</span>

            {/* Editable weight */}
            <input
              type="number"
              ref={set.id === newSetId ? weightInputRef : null}
              className="w-18 text-center bg-gray-700 text-white rounded no-spin"
              value={formatNumber(set.weight)}
              onChange={(e) =>
                handleSetChange(set.id, "weight", e.target.value)
              }
              onBlur={() => {
                if (set.id === newSetId) {
                  handleNewSetBlur(set);
                } else {
                  updateSet(
                    set.id,
                    set.reps,
                    sets.find((s) => s.id === set.id).weight
                  );
                }
              }}
              step="0.5"
            />
            <span>LBS</span>

            {/* Delete button */}
            {showDeleteButton && (
              <button
                type="button"
                onClick={() => {
                  setSetToDelete(set);
                  setShowDeleteModal(true);
                }}
                className="text-red-500 hover:text-red-700 px-2"
                aria-label="Delete set"
              >
                🗑️
              </button>
            )}
          </div>
        ))}
      </div>

      {/* DELETE CONFIRMATION MODAL */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-900 text-white rounded p-6 max-w-sm w-full">
            <h2 className="text-lg font-semibold mb-4">Confirm Delete</h2>
            <p>Are you sure you want to delete this set?</p>
            <div className="mt-6 flex justify-end space-x-4">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 rounded border border-gray-600 hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  deleteSet(setToDelete.id);
                  setShowDeleteModal(false);
                }}
                className="px-4 py-2 rounded bg-red-600 hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create New Set Button */}
      <button
        onClick={handleAddNewSet}
        className="mt-4 bg-blue-600 hover:bg-blue-700 text-white rounded px-4 py-2"
      >
        New Set
      </button>
    </div>
  );
}
