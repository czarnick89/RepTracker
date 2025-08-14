import React, { useState, useRef, useEffect } from "react";
import api from "../api/axiosRefreshInterceptor";
import { exerciseNames } from "../data/exerciseNames";
import InfoModal from "./InfoModal";
import { getExerciseByName, getExerciseGifUrl } from "../api/exerciseDB";

export default function ExerciseCard({
  exercise,
  onExerciseNameSave,
  onDelete,
  showDeleteButton,
  onWeightPreferenceChange,
}) {
  const [exerciseName, setExerciseName] = useState(exercise.name);
  // For sets, keep track of reps and weight locally too:
  const [sets, setSets] = useState(exercise.sets);
  // Track which set is new and pending save
  const [newSetId, setNewSetId] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [setToDelete, setSetToDelete] = useState(null);

  const [filteredExercises, setFilteredExercises] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);

  const [isInfoModalOpen, setIsInfoModalOpen] = useState(false);
  const [exerciseInfo, setExerciseInfo] = useState(null);
  const [loadingInfo, setLoadingInfo] = useState(false);
  const [errorInfo, setErrorInfo] = useState(null);

  const [cooldown, setCooldown] = useState(0);

  const selectingFromDropdownRef = useRef(false);

  const weightInputRef = useRef(null);
  const exerciseInfoCache = useRef({});

  // Add a useEffect to sync local exerciseName when exercise prop changes (e.g., after saving new exercise)
  useEffect(() => {
    setExerciseName(exercise.name);
    setSets(exercise.sets);
  }, [exercise]);

  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  const handleExerciseNameBlur = () => {
    if (selectingFromDropdownRef.current) {
      // Just selected from dropdown, skip this blur save
      selectingFromDropdownRef.current = false;
      return;
    }

    // Always close the dropdown on blur
    setShowDropdown(false);

    if (exerciseName === exercise.name) return;

    if (onExerciseNameSave) {
      onExerciseNameSave(exercise, exerciseName);
    }
  };

  const handleExerciseNameChange = (e) => {
    const input = e.target.value;
    setExerciseName(input);

    if (input.length >= 2) {
      const filtered = exerciseNames.filter((name) =>
        name.toLowerCase().includes(input.toLowerCase())
      );
      setFilteredExercises(filtered);
      setShowDropdown(true);
    } else {
      setFilteredExercises([]);
      setShowDropdown(false);
    }
  };

  const updateSet = (setId, newReps, newWeight) => {
    if (setId < 0) return; // don't PATCH sets that haven't been created yet

    api
      .patch(
        `${import.meta.env.VITE_BACKEND_URL}/api/v1/workouts/sets/${setId}/`,
        { reps: Number(newReps), weight: normalizeWeight(newWeight) },
        { withCredentials: true }
      )
      .catch((err) => console.error("Failed to update set", err));
  };

  const createNewSet = async (reps, weight) => {
    try {
      const res = await api.post(
        `${import.meta.env.VITE_BACKEND_URL}/api/v1/workouts/sets/`,
        {
          exercise: exercise.id,
          reps: Number(reps),
          weight: normalizeWeight(weight),
        },
        { withCredentials: true }
      );
      return res.data;
    } catch (err) {
      console.error("Failed to create new set", err);
      throw err;
    }
  };

  const deleteSet = (setId) => {
    if (setId < 0) {
      // Remove locally
      setSets((prev) => prev.filter((s) => s.id !== setId));
      if (newSetId === setId) setNewSetId(null);
      return;
    }

    api
      .delete(`${import.meta.env.VITE_BACKEND_URL}/api/v1/workouts/sets/${setId}/`, {
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

  const fetchExerciseInfo = async (name) => {
    if (!name || name.trim() === "") {
      setErrorInfo("Please enter an exercise name");
      setExerciseInfo(null);
      return;
    }

    const lowerName = name.toLowerCase();

    if (exerciseInfoCache.current[lowerName]) {
      setExerciseInfo(exerciseInfoCache.current[lowerName]);
      setErrorInfo(null);
      setLoadingInfo(false);
      return;
    }

    setLoadingInfo(true);
    setErrorInfo(null);

    try {
      const data = await getExerciseByName(lowerName);
      if (data.length > 0) {
        exerciseInfoCache.current[lowerName] = data[0];
        setExerciseInfo(data[0]);
        setErrorInfo(null);
      } else {
        setExerciseInfo(null);
        setErrorInfo("No exercise found");
      }
    } catch (err) {
      setErrorInfo(err.message);
      setExerciseInfo(null);
    } finally {
      setLoadingInfo(false);
    }
  };

  const handleInfoClick = () => {
    setCooldown(5);
    fetchExerciseInfo(exerciseName);
    setIsInfoModalOpen(true);
  };

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
    <div className="bg-gray-800 rounded-md p-4 m-2 flex-grow min-w-[200px] max-w-[340px] border border-gray-600">
      <div className="relative mb-4 w-full">
        <div className="flex items-center gap-2 w-full">
          {/* Info button */}
          <button
            type="button"
            aria-label="Show exercise info"
            onClick={handleInfoClick}
            className="text-blue-400 hover:text-blue-600 font-bold px-2 py-1 flex-shrink-0 w-8"
            disabled={loadingInfo || cooldown > 0}
          >
            {cooldown > 0 ? cooldown : "?"}
          </button>

          {/* Exercise name input */}
          <input
            type="text"
            value={exerciseName}
            onChange={handleExerciseNameChange}
            onBlur={handleExerciseNameBlur}
            className="bg-gray-700 text-white font-semibold text-center rounded px-2 py-1 flex-grow min-w-[100px] max-w-[500px] overflow-x-auto"
          />

          {/* Weight change dropdown */}
          <select
            value={exercise.weight_change_preference}
            onChange={(e) =>
              onWeightPreferenceChange(exercise.id, e.target.value)
            }
            className="bg-gray-700 text-white font-semibold text-center rounded px-0 py-1 w-6 appearance-none flex-shrink-0"
          >
            <option value="increase">⬆️</option>
            <option value="same">➖</option>
            <option value="decrease">⬇️</option>
          </select>

          {/* Optional trash button */}
          {showDeleteButton && (
            <button
              onClick={onDelete}
              className="text-red-600 hover:text-red-800 font-bold px-3 py-1 rounded flex-shrink-0"
              aria-label={`Delete exercise ${exerciseName}`}
              type="button"
            >
              🗑️
            </button>
          )}
        </div>

        <InfoModal
          isOpen={isInfoModalOpen}
          onClose={() => setIsInfoModalOpen(false)}
        >
          {loadingInfo ? (
            <p>Loading exercise info...</p>
          ) : errorInfo ? (
            <p className="text-red-500">{errorInfo}</p>
          ) : exerciseInfo ? (
            <div className="space-y-4">
              <img
                src={getExerciseGifUrl(exerciseInfo.id)}
                alt={`${exerciseInfo.name} animation`}
                className="w-full rounded"
              />

              <h2 className="text-2xl font-bold capitalize">
                {exerciseInfo.name}
              </h2>
              <p className="text-sm text-gray-300">
                <strong>Target:</strong> {exerciseInfo.target}
              </p>
              <p className="text-sm text-gray-300">
                <strong>Secondary Muscles:</strong>{" "}
                {exerciseInfo.secondaryMuscles.join(", ")}
              </p>
              {exerciseInfo.description && (
                <p className="text-base">{exerciseInfo.description}</p>
              )}
              {exerciseInfo.instructions && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">Instructions</h3>
                  <ol className="list-decimal list-inside space-y-1">
                    {exerciseInfo.instructions.map((step, index) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          ) : (
            <p>No exercise data to show.</p>
          )}
        </InfoModal>

        {showDropdown && filteredExercises.length > 0 && (
          <ul className="absolute top-full left-0 right-0 bg-gray-800 border border-gray-600 max-h-48 overflow-auto mt-1 z-50 rounded shadow-lg">
            {filteredExercises.map((name, idx) => (
              <li
                key={idx}
                className="px-3 py-1 hover:bg-gray-600 cursor-pointer"
                onMouseDown={() => {
                  selectingFromDropdownRef.current = true;
                  setExerciseName(name);
                  setShowDropdown(false);
                  if (onExerciseNameSave) onExerciseNameSave(exercise, name);
                }}
              >
                {name}
              </li>
            ))}
          </ul>
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
      <div className="flex justify-center mt-4">
        <button
          onClick={handleAddNewSet}
          className="mt-4 bg-blue-600 hover:bg-blue-700 text-white rounded px-4 py-2"
        >
          New Set
        </button>
      </div>
    </div>
  );
}
