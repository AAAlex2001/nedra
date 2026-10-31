"use client";

import { useEffect, useState, type MouseEvent } from "react";
import type { TocItem } from "@/entities/article";

const READING_LINE = 140;

const findHeadings = (items: TocItem[]): HTMLElement[] => {
  const headings: HTMLElement[] = [];

  for (const item of items) {
    const heading = document.getElementById(item.id);
    if (heading) headings.push(heading);
  }

  return headings;
};

export const useActiveHeading = (items: TocItem[]) => {
  const [activeId, setActiveId] = useState(items[0]?.id ?? "");

  useEffect(() => {
    const headings = findHeadings(items);
    if (headings.length === 0) return;

    let frame = 0;

    const updateActive = () => {
      frame = 0;
      let current = headings[0].id;

      for (const heading of headings) {
        if (heading.getBoundingClientRect().top <= READING_LINE) current = heading.id;
      }

      setActiveId(current);
    };

    const scheduleUpdate = () => {
      if (frame) return;
      frame = window.requestAnimationFrame(updateActive);
    };

    scheduleUpdate();
    window.addEventListener("scroll", scheduleUpdate, { passive: true });
    window.addEventListener("resize", scheduleUpdate);

    return () => {
      if (frame) window.cancelAnimationFrame(frame);
      window.removeEventListener("scroll", scheduleUpdate);
      window.removeEventListener("resize", scheduleUpdate);
    };
  }, [items]);

  const selectHeading = (event: MouseEvent<HTMLAnchorElement>, id: string) => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;

    const heading = document.getElementById(id);
    if (!heading) return;

    event.preventDefault();
    setActiveId(id);
    window.history.replaceState(null, "", `#${id}`);
    heading.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return { activeId, selectHeading };
};
