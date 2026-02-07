import { useEffect, useState } from "react";

/**
 * Custom hook that tracks scroll position to detect when user has scrolled past a threshold.
 * Useful for navbar effects like backdrop blur or shadow.
 *
 * @param threshold - Scroll Y position threshold (default: 50)
 * @returns Boolean indicating if scrolled past threshold
 *
 * @example
 * const scrolled = useScrollPosition();
 * <nav className={scrolled ? 'bg-white/80 backdrop-blur-lg' : 'bg-transparent'}>
 */
export function useScrollPosition(threshold: number = 50) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > threshold);
    };

    // Add event listener with passive option for better performance
    window.addEventListener("scroll", handleScroll, { passive: true });

    // Check initial scroll position
    handleScroll();

    // Cleanup
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [threshold]);

  return scrolled;
}
