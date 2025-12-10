import { useState, useEffect, useRef } from "react";

// Accordion component that can expand/collapse its content
export default function Accordion({ title, children }) {
  const [open, setOpen] = useState(false); // track whether accordion is open
  const [isSticky, setIsSticky] = useState(false); // track if title should be sticky
  const containerRef = useRef(null); // ref for the accordion container
  const contentRef = useRef(null); // ref for the content area
  const titleRef = useRef(null); // ref for the title element

  // Toggle open/closed state
  const toggleOpen = () => setOpen((prev) => !prev);

  // Handle keyboard accessibility: toggle on Enter key
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      toggleOpen();
    }
  };

  // Intersection observer to manage sticky title behavior
  useEffect(() => {
    if (!open) {
      setIsSticky(false);
      return;
    }

    const handleScroll = () => {
      if (!containerRef.current || !titleRef.current || !contentRef.current) return;

      const navbarHeight = 64; // Navbar height with padding (p-4 = 1rem = 16px top + 16px bottom + text/content)
      const containerRect = containerRef.current.getBoundingClientRect();
      const contentRect = contentRef.current.getBoundingClientRect();
      
      // Title should be sticky when:
      // 1. The container top is above the navbar bottom
      // 2. The content bottom is still below the navbar (we're still scrolling through this workout)
      const containerTopAboveNavbar = containerRect.top < navbarHeight;
      const contentBottomBelowNavbar = contentRect.bottom > navbarHeight + 50; // 50 = approximate title height
      
      setIsSticky(containerTopAboveNavbar && contentBottomBelowNavbar);
    };

    // Initial check
    handleScroll();

    // Listen to scroll events
    window.addEventListener('scroll', handleScroll);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [open]);

  return (
    <div ref={containerRef} className="border rounded mb-2 w-[100%] max-w-[4xl] mx-auto">
      {/* Sticky title when scrolling through content */}
      <div
        ref={titleRef}
        role="button"
        tabIndex={0}
        className={`w-full px-4 py-2 text-left bg-gray-700 hover:bg-gray-600 focus:outline-none cursor-pointer select-none transition-all ${
          isSticky && open ? 'sticky top-[72px] z-20 shadow-lg' : ''
        }`}
        onClick={toggleOpen}
        onKeyDown={handleKeyDown}
        aria-expanded={open}
      >
        {title}
      </div>
      {open && (
        <div ref={contentRef} className="p-4 bg-gray-800 text-white w-full">{children}</div>
      )}
    </div>
  );
}
