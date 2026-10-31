"use client";

import { useEffect, useRef, useState } from "react";

const BUTTON_SIZE = 36;
const TEXT_GAP = 16;
const EDGE_GAP = 4;
const DESKTOP_WIDTH = 1440;

type FloatingPosition = {
  left: number;
  visible: boolean;
};

const HIDDEN: FloatingPosition = { left: 0, visible: false };

export const useFloatingPosition = () => {
  const rootRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState<FloatingPosition>(HIDDEN);

  useEffect(() => {
    const measure = () => {
      const main = rootRef.current?.closest("[data-article-main]");

      if (!main || window.innerWidth < DESKTOP_WIDTH) {
        setPosition(HIDDEN);
        return;
      }

      const mainRect = main.getBoundingClientRect();
      const center = window.innerHeight / 2;
      const readingArticle = mainRect.top < center && mainRect.bottom > center;

      const besideText = mainRect.right + TEXT_GAP;
      const left = Math.min(besideText, window.innerWidth - BUTTON_SIZE - EDGE_GAP);

      setPosition({ left, visible: readingArticle });
    };

    measure();
    window.addEventListener("scroll", measure, { passive: true });
    window.addEventListener("resize", measure);

    return () => {
      window.removeEventListener("scroll", measure);
      window.removeEventListener("resize", measure);
    };
  }, []);

  return { rootRef, position };
};
