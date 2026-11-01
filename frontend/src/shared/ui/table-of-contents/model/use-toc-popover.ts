"use client";

import { useEffect, useRef, useState, type PointerEvent } from "react";

const CLOSE_DELAY = 300;

export const useTocPopover = () => {
  const [open, setOpen] = useState(false);
  const [pinned, setPinned] = useState(false);
  const popoverRef = useRef<HTMLDivElement>(null);
  const closeTimer = useRef<number | null>(null);

  const cancelClose = () => {
    if (closeTimer.current === null) return;

    window.clearTimeout(closeTimer.current);
    closeTimer.current = null;
  };

  const close = () => {
    cancelClose();
    setPinned(false);
    setOpen(false);
  };

  useEffect(() => {
    if (!open) return;

    const closeNow = () => {
      if (closeTimer.current !== null) window.clearTimeout(closeTimer.current);
      closeTimer.current = null;
      setPinned(false);
      setOpen(false);
    };

    const closeOnOutside = (event: globalThis.PointerEvent) => {
      if (popoverRef.current?.contains(event.target as Node)) return;
      closeNow();
    };

    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeNow();
    };

    document.addEventListener("pointerdown", closeOnOutside);
    document.addEventListener("keydown", closeOnEscape);

    return () => {
      document.removeEventListener("pointerdown", closeOnOutside);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [open]);

  useEffect(() => {
    return () => {
      if (closeTimer.current !== null) window.clearTimeout(closeTimer.current);
    };
  }, []);

  const show = (event: PointerEvent<HTMLElement>) => {
    cancelClose();
    if (event.pointerType === "touch") return;
    setOpen(true);
  };

  const leave = () => {
    if (pinned) return;

    cancelClose();
    closeTimer.current = window.setTimeout(() => setOpen(false), CLOSE_DELAY);
  };

  const toggle = () => {
    if (pinned) {
      close();
      return;
    }

    cancelClose();
    setPinned(true);
    setOpen(true);
  };

  return { open, popoverRef, show, leave, toggle, close };
};
