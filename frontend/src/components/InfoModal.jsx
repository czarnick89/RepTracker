
export default function InfoModal({ isOpen, onClose, children }) {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      ></div>

      {/* Modal content */}
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div
          className="bg-gray-800 text-white rounded-lg max-w-md w-full max-h-[80vh] overflow-y-auto p-6 relative"
          onClick={(e) => e.stopPropagation()} // Prevent closing modal when clicking inside
        >
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-2 right-2 text-gray-400 hover:text-white font-bold text-xl"
            aria-label="Close modal"
            type="button"
          >
            &times;
          </button>

          {/* Modal content */}
          {children}
        </div>
      </div>
    </>
  );
}
