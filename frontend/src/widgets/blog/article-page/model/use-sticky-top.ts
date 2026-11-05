"use client";

import { useEffect, useRef, useState } from "react";
import { useSession } from "@/entities/user";

const HEADER_OFFSET = 100;
const GUEST_BAR_OFFSET = 120;
const SCREEN_EDGE_OFFSET = 24;

export const useStickyTop = () => {
  const ref = useRef<HTMLElement>(null);
  const [top, setTop] = useState(HEADER_OFFSET);
  const { status } = useSession();

  const bottomOffset = status === "anonymous" ? GUEST_BAR_OFFSET : SCREEN_EDGE_OFFSET;

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const measure = () => {
      const centeredTop = (window.innerHeight - element.offsetHeight) / 2;
      const bottomAlignedTop = window.innerHeight - bottomOffset - element.offsetHeight;
      setTop(Math.min(Math.max(HEADER_OFFSET, centeredTop), bottomAlignedTop));
    };

    const observer = new ResizeObserver(measure);
    observer.observe(element);
    window.addEventListener("resize", measure);
    measure();

    return () => {
      observer.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, [bottomOffset]);

  const maxHeight = `calc(100dvh - ${HEADER_OFFSET + bottomOffset}px)`;

  return { ref, top, maxHeight };
};
