import { useState, useRef, useEffect } from "react";
import api from "../api/axiosRefreshInterceptor";
import { exerciseNames } from "../data/exerciseNames";
import InfoModal from "./InfoModal";
import Loading from "./Loading";
import { getExerciseByName, getExerciseGifUrl } from "../api/exerciseDB";

export default function ExerciseCard({
  exercise,
  onExerciseNameSave,
  onDelete,
  showDeleteButton,
  onWeightPreferenceChange,
  autoFocus,
  onAutoFocusComplete,
}) {
  const [exerciseName, setExerciseName] = useState(exercise.name); // State for exercise name
  const [sets, setSets] = useState(exercise.sets); // Local copy of sets to update UI, actual update of these values happen?
  const [newSetId, setNewSetId] = useState(null); // Tracks which set is new and pending save
  const [showDeleteModal, setShowDeleteModal] = useState(false); // Track if delete modal for sets is open
  const [setToDelete, setSetToDelete] = useState(null); // Holds set to delete during delete flow

  const [filteredExercises, setFilteredExercises] = useState([]); // Auto-suggest dropdown state, list of exercises
  const [showDropdown, setShowDropdown] = useState(false); // Dropdown state, not showing by default

  const [isInfoModalOpen, setIsInfoModalOpen] = useState(false); // Exercise info modal show state
  const [exerciseInfo, setExerciseInfo] = useState(null); // Exercise info modal data from exerciseDB api call
  const [loadingInfo, setLoadingInfo] = useState(false);
  const [errorInfo, setErrorInfo] = useState(null);

  const [cooldown, setCooldown] = useState(0); // Cooldown state so you can't spam click info button

  const selectingFromDropdownRef = useRef(false); // Flag to prevent blur-triggered save when selecting from dropdown

  const weightInputRef = useRef(null); // Ref for weight input for potential programmatic focus
  const repsInputRef = useRef(null); // Ref for reps input to check focus transitions
  const nameInputRef = useRef(null); // Ref for the exercise name input so we can focus it
  const focusTimerRef = useRef(null);

  const exerciseInfoCache = useRef({}); // Cache exercise info to avoid redundant API calls

  // Cooldown timer effect for question mark button
  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  // Save exercise name on blur UNLESS selecting from dropdown
  const handleExerciseNameBlur = () => {
    if (selectingFromDropdownRef.current) {
      // If User just selected from dropdown, skip this blur save
      selectingFromDropdownRef.current = false;
      return;
    }

    // Always close the dropdown on blur
    setShowDropdown(false);

    // Just return if the name didn't change
    if (exerciseName === exercise.name) return;

    //
    if (onExerciseNameSave) {
      onExerciseNameSave(exercise, exerciseName); // Save exercise name via parent function
    }
  };

  // Focus name input when parent requests via autoFocus prop
  useEffect(() => {
    if (autoFocus && nameInputRef.current) {
      nameInputRef.current.focus();
      // Move caret to end
      const val = nameInputRef.current.value;
      nameInputRef.current.setSelectionRange(val.length, val.length);
      if (onAutoFocusComplete) onAutoFocusComplete();
    }
  }, [autoFocus, onAutoFocusComplete]);

  // Handle typing in exercise name input and filter dropdown suggestions
  const handleExerciseNameChange = (e) => {
    const input = e.target.value;
    setExerciseName(input); // Set exercise name to input

    if (input.length >= 2) {
      // Once input is 2 or greater, start filtering the list of exercises
      const filtered = exerciseNames.filter((name) =>
        name.toLowerCase().includes(input.toLowerCase())
      );
      setFilteredExercises(filtered); // Save the filtered exercise list in state
      setShowDropdown(true); // Show the drop down
    } else {
      // Don't filter or show dropdown if input.length < 2
      setFilteredExercises([]);
      setShowDropdown(false);
    }
  };

  // Update a set on the server
  const updateSet = (setId, newReps, newWeight) => {
    if (setId < 0) return; // don't PATCH sets that haven't been created yet

    api
      .patch(
        // Use api to request the backend update the set reps, weight, or both
        `${import.meta.env.VITE_BACKEND_URL}/api/v1/workouts/sets/${setId}/`,
        { reps: Number(newReps), weight: normalizeWeight(newWeight) }
      )
      .catch((err) => console.error("Failed to update set", err));
  };

  // Create a new set on the backend
  const createNewSet = async (reps, weight) => {
    try {
      const res = await api.post(
        // Send request to backend with necessary info to create a new set
        `${import.meta.env.VITE_BACKEND_URL}/api/v1/workouts/sets/`,
        {
          exercise: exercise.id,
          reps: Number(reps),
          weight: normalizeWeight(weight),
        }
      );
      return res.data; // return the newly created set for front end updating
    } catch (err) {
      console.error("Failed to create new set", err);
      throw err;
    }
  };

  // Delete a set either locally or from backend
  const deleteSet = (setId) => {
    if (setId < 0) {
      // Remove locally
      setSets((prev) => prev.filter((s) => s.id !== setId));
      if (newSetId === setId) setNewSetId(null);
      return;
    }

    api
      .delete(
        // Send delete request to backend for set
        `${import.meta.env.VITE_BACKEND_URL}/api/v1/workouts/sets/${setId}/`)
      .then(() => {
        setSets((prev) => prev.filter((s) => s.id !== setId)); // remove set from local state after delete on back end
      })
      .catch((err) => console.error("Failed to delete set", err));
  };

  // Handle reps or weight change locally
  const handleSetChange = (setId, field, value) => {
    setSets((prev) =>
      prev.map((s) => (s.id === setId ? { ...s, [field]: value } : s))
    );
  };

  // Handle add new set on front end
  const handleAddNewSet = () => {
    // Create a temp set id for local tracking (negative to avoid clashing)
    const tempId = Math.min(...sets.map((s) => s.id), 0) - 1;
    const blankSet = { id: tempId, reps: "", weight: "" };
    setSets((prev) => [...prev, blankSet]); // Add new set to state
    setNewSetId(tempId); // Keep track of the temp id

    // Workaround for mobile: many mobile browsers will only open the keyboard
    // if focus is called synchronously inside the user gesture event handler.
    // The new weight input isn't in the DOM yet, so focus the already-mounted
    // name input synchronously to open the keyboard, then the effect that
    // focuses the weight input after render will transfer focus to it.
    if (nameInputRef.current) {
      try {
        nameInputRef.current.focus();
        const v = nameInputRef.current.value || "";
        nameInputRef.current.setSelectionRange(v.length, v.length);
      } catch (e) {
        // ignore
      }
    }
  };

  // When a newSetId is set, attempt to focus the weight input reliably after render.
  useEffect(() => {
    if (newSetId == null) return;

    // Wait for the browser to render the new input. Use rAF then a small timeout
    const raf = requestAnimationFrame(() => {
      focusTimerRef.current = setTimeout(() => {
        if (weightInputRef.current) {
          try {
            weightInputRef.current.focus();
            const val = weightInputRef.current.value || "";
            weightInputRef.current.setSelectionRange(val.length, val.length);
          } catch (e) {
            // ignore focus errors
          }
        }
      }, 30);
    });

    return () => {
      cancelAnimationFrame(raf);
      if (focusTimerRef.current) {
        clearTimeout(focusTimerRef.current);
        focusTimerRef.current = null;
      }
    };
  }, [newSetId]); // Removed 'sets' dependency to prevent refocusing on every keystroke

  // Fetch exercise info from API or cache
  const fetchExerciseInfo = async (name) => {
    if (!name || name.trim() === "") {
      setErrorInfo("Please enter an exercise name");
      setExerciseInfo(null);
      return;
    }

    const lowerName = name.toLowerCase();

    // Pull from cache if available
    if (exerciseInfoCache.current[lowerName]) {
      setExerciseInfo(exerciseInfoCache.current[lowerName]);
      setErrorInfo(null);
      setLoadingInfo(false);
      return;
    }

    setLoadingInfo(true);
    setErrorInfo(null);

    // If the exercise name wasn't in the cache
    try {
      // Use getExerciseByName to backend proxy the exerciseDB
      const data = await getExerciseByName(lowerName);
      if (data.length > 0) {
        exerciseInfoCache.current[lowerName] = data[0]; // pull the name of the first exercise object returned
        setExerciseInfo(data[0]); // Store the data from the API call in state
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

  // Handle info button click (question mark button)
  const handleInfoClick = () => {
    setCooldown(5);
    fetchExerciseInfo(exerciseName);
    setIsInfoModalOpen(true);
  };

  // Validate reps input
  const isValidReps = (val) => {
    const num = Number(val);
    return Number.isInteger(num) && num > 0;
  };

  // Validate weight input
  const isValidWeight = (val) => {
    const num = Number(String(val).replace(",", "."));
    return !isNaN(num) && num >= 0;
  };

  // Format numbers nicely for display
  const formatNumber = (num) => {
    if (num == null) return "";

    // If it's a string, try to determine if it's user typing or a numeric string we can normalize
    if (typeof num === "string") {
      const s = num.trim();
      if (s === "") return "";

      // If user is in the middle of typing a decimal point (e.g. '1.' or '1,') leave it as-is
      if (/[.,]$/.test(s)) return s;

      // If the string is purely numeric (optional decimal with digits), normalize it
      if (/^-?\d+(?:[.,]\d+)?$/.test(s)) {
        const parsed = Number(s.replace(",", "."));
        if (Number.isInteger(parsed)) return parsed.toString();
        // Use 2 decimal places max, then strip trailing zeros (and trailing dot)
        return parsed.toFixed(2).replace(/\.?0+$/, "");
      }

      // Otherwise leave non-numeric strings untouched
      return s;
    }

    // For numeric values, format: integer as-is, otherwise up to 2 decimals without trailing zeros
    const n = Number(num);
    if (Number.isNaN(n)) return "";
    return Number.isInteger(n) ? n.toString() : n.toFixed(2).replace(/\.?0+$/, "");
  };

  // Handle blur event on a new set to save it to backend
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
            // Add logic to keep or discard 
          });
      }
    }
  };

  // Convert empty or invalid weight to 0
  const normalizeWeight = (weight) => {
    if (weight === "" || weight === null || weight === undefined) return 0;
    // Accept comma as decimal separator (mobile keyboards/locales may use comma)
    const parsed = parseFloat(String(weight).replace(",", "."));
    return isNaN(parsed) ? 0 : parsed;
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
            ref={nameInputRef}
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
            <Loading message="Loading exercise info..." fullscreen={false} />
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
              ref={set.id === newSetId ? repsInputRef : null}
              className="w-10 text-center bg-gray-700 text-white rounded no-spin"
              value={formatNumber(set.reps)}
              onChange={(e) => handleSetChange(set.id, "reps", e.target.value)}
              onBlur={(e) => {
                if (set.id === newSetId) {
                  // Only submit if focus is leaving the form (not moving to weight input)
                  if (e.relatedTarget !== weightInputRef.current) {
                    handleNewSetBlur(set);
                  }
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
              onBlur={(e) => {
                if (set.id === newSetId) {
                  // Only submit if focus is leaving the form (not moving to reps input)
                  if (e.relatedTarget !== repsInputRef.current) {
                    handleNewSetBlur(set);
                  }
                } else {
                  updateSet(
                    set.id,
                    set.reps,
                    sets.find((s) => s.id === set.id).weight
                  );
                }
              }}
              step="any"
              inputMode="decimal"
              pattern="^[0-9]*[.,]?[0-9]+$"
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
