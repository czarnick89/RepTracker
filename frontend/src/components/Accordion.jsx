import { useState } from "react";

export default function Accordion({ title, children }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border rounded mb-2">
      <button
        className="w-full px-4 py-2 text-left bg-gray-700 hover:bg-gray-600 focus:outline-none"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
      >
        {title}
      </button>
      {open && (
        <div className="p-4 bg-gray-800 text-white">
          {children}
        </div>
      )}
    </div>
  );
}
