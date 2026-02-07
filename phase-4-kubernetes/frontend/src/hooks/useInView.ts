import { useEffect, useRef, useState } from "react";

/**
 * Custom hook that uses Intersection Observer to detect when an element enters the viewport.
 * Useful for triggering scroll-based animations.
 *
 * @param options - Optional Intersection Observer options
 * @returns Object with ref to attach to element and isInView boolean state
 *
 * @example
 * const { ref, isInView } = useInView();
 * <div ref={ref} className={isInView ? 'animate-fade-in-up' : 'opacity-0'}>
 *   Content that animates in when scrolled into view
 * </div>
 */
export function useInView(options?: IntersectionObserverInit) {
  const ref = useRef<HTMLDivElement>(null);
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        // Only trigger once when element enters viewport
        if (entry.isIntersecting) {
          setIsInView(true);
        }
      },
      {
        threshold: 0.1, // Trigger when 10% of element is visible
        ...options,
      }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    // Cleanup
    return () => {
      observer.disconnect();
    };
  }, [options]);

  return { ref, isInView };
}
