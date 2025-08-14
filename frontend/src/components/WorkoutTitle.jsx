import React from "react";
import { useState } from "react";

// 
function WorkoutTitle({ workout, onNameUpdate, onDelete, showDeleteButton}) {
  const [isEditing, setIsEditing] = useState(false); // Store isEditing state
  const [name, setName] = React.useState(workout.name); // Store name, default to workout.name

  // Called on blur
  const handleBlur = async () => {
    setIsEditing(false);
    // Only update if the name is non-empty and has changed
    if (name.trim() && name !== workout.name) {
      await onNameUpdate(workout.id, name); // Call parent handler
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      e.target.blur();
    }
  };

  return (
    <div className="flex items-center justify-between">
      {isEditing ? (
        <input
          type="text"
          value={name}
          autoFocus
          onClick={(e) => e.stopPropagation()}
          onChange={(e) => setName(e.target.value)}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          className="bg-gray-700 text-white font-semibold rounded px-2 py-1 w-full"
        />
      ) : (
        <span
          className="cursor-pointer font-semibold"
          onClick={() => setIsEditing(true)}
          title="Click to edit workout name"
        >
          {name} -{" "}
          {(() => {
            const [year, month, day] = workout.date.split("-");
            const dateObj = new Date(year, month - 1, day);
            return dateObj.toLocaleDateString();
          })()}
        </span>
      )}
{showDeleteButton && (
      <button
        onClick={() => onDelete(workout.id)}
        className="ml-2 text-red-600 hover:text-red-800 font-bold"
        title="Delete workout"
        aria-label={`Delete workout ${name}`}
      >
        🗑️
      </button>)}
    </div>
  );
}

export default WorkoutTitle;
