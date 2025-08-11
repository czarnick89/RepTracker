import { useState } from "react";

export default function Accordion({ title, children }) {
  const [open, setOpen] = useState(false);

  const toggleOpen = () => setOpen((prev) => !prev);

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      toggleOpen();
    }
  };

  return (
    <div className="border rounded mb-2">
      <div
        role="button"
        tabIndex={0}
        className="w-full px-4 py-2 text-left bg-gray-700 hover:bg-gray-600 focus:outline-none cursor-pointer select-none"
        onClick={toggleOpen}
        onKeyDown={handleKeyDown}
        aria-expanded={open}
      >
        {title}
      </div>
      {open && (
        <div className="p-4 bg-gray-800 text-white">
          {children}
        </div>
      )}
    </div>
  );
}
