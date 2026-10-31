"use client";

import { useEffect, useRef, useState } from "react";

const HEADER_OFFSET = 110;
const BOTTOM_OFFSET = 120;

export const useStickyTop = () => {
  const ref = useRef<HTMLElement>(null);
  const [top, setTop] = useState(HEADER_OFFSET);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const measure = () => {
      const bottomAlignedTop = window.innerHeight - BOTTOM_OFFSET - element.offsetHeight;
      setTop(Math.min(HEADER_OFFSET, bottomAlignedTop));
    };

    const observer = new ResizeObserver(measure);
    observer.observe(element);
    window.addEventListener("resize", measure);
    measure();

    return () => {
      observer.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, []);

  return { ref, top };
};
