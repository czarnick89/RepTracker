import { useState } from "react";

// Modal for creating multiple sets at once with the same weight
export default function BulkSetModal({ isOpen, onAccept, onCancel }) {
  const [numSets, setNumSets] = useState("");
  const [weight, setWeight] = useState("");

  if (!isOpen) return null;

  const handleAccept = () => {
    const setsCount = parseInt(numSets);
    const weightValue = parseFloat(weight);
    
    if (isNaN(setsCount) || setsCount <= 0) {
      alert("Please enter a valid number of sets (must be greater than 0)");
      return;
    }
    
    if (isNaN(weightValue) || weightValue < 0) {
      alert("Please enter a valid weight (must be 0 or greater)");
      return;
    }
    
    onAccept(setsCount, weightValue);
    // Reset form
    setNumSets("");
    setWeight("");
  };

  const handleCancel = () => {
    // Reset form
    setNumSets("");
    setWeight("");
    onCancel();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 text-white p-6 rounded shadow max-w-sm w-full">
        <h2 className="text-xl font-semibold mb-4">Quick Set Creation</h2>
        <p className="mb-4 text-gray-300">
          Create multiple sets at once with the same weight.
        </p>
        
        <div className="mb-4">
          <label htmlFor="numSets" className="block mb-2 text-sm font-medium">
            Number of Sets
          </label>
          <input
            id="numSets"
            type="number"
            min="1"
            value={numSets}
            onChange={(e) => setNumSets(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            placeholder="e.g., 3"
            autoFocus
          />
        </div>
        
        <div className="mb-6">
          <label htmlFor="weight" className="block mb-2 text-sm font-medium">
            Weight (lbs)
          </label>
          <input
            id="weight"
            type="number"
            min="0"
            step="0.5"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            placeholder="e.g., 135"
          />
        </div>
        
        <div className="flex justify-end space-x-4">
          <button
            onClick={handleCancel}
            className="px-4 py-2 rounded border border-gray-400 hover:bg-gray-700"
          >
            Cancel
          </button>
          <button
            onClick={handleAccept}
            className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700"
          >
            Accept
          </button>
        </div>
      </div>
    </div>
  );
}
