import React from "react";

function WorkoutTitle({ workout, onNameUpdate, onDelete, showDeleteButton}) {
  const [isEditing, setIsEditing] = React.useState(false);
  const [name, setName] = React.useState(workout.name);

  const handleBlur = async () => {
    setIsEditing(false);
    if (name.trim() && name !== workout.name) {
      await onNameUpdate(workout.id, name);
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
