"use client";

/**
 * Reusable Modal component for dialogs and overlays.
 *
 * Client Component with:
 * - Portal-based rendering (renders outside DOM hierarchy)
 * - ESC key to close
 * - Click outside to close
 * - Backdrop blur effect
 * - Accessibility (aria-modal, role=dialog)
 * - Focus trap (future enhancement)
 */

import { useEffect } from "react";
import { createPortal } from "react-dom";
import { cn } from "@/lib/utils";

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
}

export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = "md",
}: ModalProps) {
  // Handle ESC key press
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    }

    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
      // Prevent body scroll when modal is open
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Portal ensures modal renders at document.body level
  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Content */}
      <div
        className={cn(
          "relative bg-white rounded-lg shadow-xl",
          size === "sm" ? "max-w-sm" :
          size === "lg" ? "max-w-2xl" :
          size === "xl" ? "max-w-3xl" :
          "max-w-md",
          "w-full mx-4",
          "animate-in fade-in zoom-in duration-200"
        )}
        onClick={(e) => e.stopPropagation()} // Prevent close on content click
      >
        {/* Header */}
        <div className="px-6 pt-4 pb-3 border-b border-gray-200">
          <h2
            id="modal-title"
            className="text-lg font-bold text-gray-900"
          >
            {title}
          </h2>
        </div>

        {/* Body */}
        <div className="px-6 py-3">{children}</div>

        {/* Footer (optional) */}
        {footer && (
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-lg">
            {footer}
          </div>
        )}
      </div>
    </div>,
    document.body
  );
}
