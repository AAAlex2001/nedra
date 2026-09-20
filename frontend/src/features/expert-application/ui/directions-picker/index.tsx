"use client";

import { useEffect, useRef, useState } from "react";
import type { Direction } from "@/entities/expert";
import { ChevronIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type DirectionsPickerProps = {
  directions: Direction[];
  selected: string[];
  onToggle: (code: string) => void;
};

const DirectionsPicker = ({ directions, selected, onToggle }: DirectionsPickerProps) => {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  const selectedTitles = directions
    .filter((direction) => selected.includes(direction.code))
    .map((direction) => direction.title);

  useEffect(() => {
    if (!open) return;

    const closeOnClickOutside = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    document.addEventListener("mousedown", closeOnClickOutside);
    document.addEventListener("keydown", closeOnEscape);

    return () => {
      document.removeEventListener("mousedown", closeOnClickOutside);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [open]);

  return (
    <div className={styles.field} ref={rootRef}>
      <span className={styles.label}>
        Направления работы<span className={styles.required}> *</span>
      </span>

      <button
        type="button"
        className={`${styles.control} ${open ? styles.controlOpen : ""}`}
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        <span className={styles.text}>
          {selectedTitles.length === 0 ? (
            <span className={styles.placeholder}>Выберите направления</span>
          ) : (
            <span className={styles.value}>{selectedTitles.join(", ")}</span>
          )}
        </span>

        {selectedTitles.length > 0 && (
          <span className={styles.count}>{selectedTitles.length}</span>
        )}

        <ChevronIcon className={`${styles.chevron} ${open ? styles.chevronOpen : ""}`} />
      </button>

      {open && (
        <ul className={styles.list} role="listbox" aria-multiselectable="true">
          {directions.map((direction) => {
            const checked = selected.includes(direction.code);

            return (
              <li key={direction.code}>
                <button
                  type="button"
                  role="option"
                  aria-selected={checked}
                  className={`${styles.option} ${checked ? styles.optionActive : ""}`}
                  onClick={() => onToggle(direction.code)}
                >
                  <span className={`${styles.box} ${checked ? styles.boxChecked : ""}`} aria-hidden="true">
                    {checked && (
                      <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                        <path
                          d="m2.5 6 2.5 2.5 4.5-5"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    )}
                  </span>
                  <span className={styles.optionTitle}>{direction.title}</span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

export default DirectionsPicker;
