"use client";

import classNames from "classnames";
import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { ChevronIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

export type SelectFieldOption = {
  value: string;
  label: string;
  hint?: string;
  image?: string;
};

type SelectFieldProps = {
  label: string;
  placeholder: string;
  options: SelectFieldOption[];
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  invalid?: boolean;
  compact?: boolean;
};

const SelectField = ({
  label,
  placeholder,
  options,
  value,
  onChange,
  required,
  invalid,
  compact,
}: SelectFieldProps) => {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const controlRef = useRef<HTMLButtonElement>(null);
  const [menuPosition, setMenuPosition] = useState<{
    top: number;
    left: number;
    width: number;
    maxHeight: number;
    transform: string;
  } | null>(null);

  const selected = options.find((option) => option.value === value);

  useEffect(() => {
    if (!open) return;

    const closeOnClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      if (!rootRef.current?.contains(target) && !listRef.current?.contains(target)) {
        setOpen(false);
      }
    };

    const positionMenu = () => {
      const control = controlRef.current;
      if (!control) return;

      const bounds = control.getBoundingClientRect();
      const spaceBelow = window.innerHeight - bounds.bottom - 14;
      const spaceAbove = bounds.top - 14;
      const openAbove = spaceBelow < 200 && spaceAbove > spaceBelow;
      const maxHeight = Math.max(0, Math.min(320, openAbove ? spaceAbove : spaceBelow));

      setMenuPosition({
        top: openAbove ? bounds.top - 6 : bounds.bottom + 6,
        left: bounds.left,
        width: bounds.width,
        maxHeight,
        transform: openAbove ? "translateY(-100%)" : "none",
      });
    };

    const repositionOnScroll = (event: Event) => {
      if (!listRef.current?.contains(event.target as Node)) positionMenu();
    };

    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
        controlRef.current?.focus();
      }
    };

    positionMenu();
    document.addEventListener("mousedown", closeOnClickOutside);
    document.addEventListener("keydown", closeOnEscape);
    window.addEventListener("scroll", repositionOnScroll, true);
    window.addEventListener("resize", positionMenu);

    return () => {
      document.removeEventListener("mousedown", closeOnClickOutside);
      document.removeEventListener("keydown", closeOnEscape);
      window.removeEventListener("scroll", repositionOnScroll, true);
      window.removeEventListener("resize", positionMenu);
    };
  }, [open]);

  return (
    <div
      className={classNames(styles.field, invalid && styles.invalid, compact && styles.compact)}
      ref={rootRef}
    >
      {!compact && (
        <span className={styles.label}>
          {label}
          {required && <span className={styles.required}> *</span>}
        </span>
      )}

      <button
        ref={controlRef}
        type="button"
        className={classNames(styles.control, open && styles.controlOpen)}
        aria-label={compact ? label : undefined}
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        {selected?.image && (
          <span className={styles.avatar}>
            <Image src={selected.image} alt="" fill sizes="40px" />
          </span>
        )}

        <span className={styles.text}>
          {selected ? (
            <>
              <span className={styles.title}>{selected.label}</span>
              {selected.hint && <span className={styles.hint}>{selected.hint}</span>}
            </>
          ) : (
            <span className={styles.placeholder}>{placeholder}</span>
          )}
        </span>

        <ChevronIcon
          className={classNames(styles.chevron, open && styles.chevronOpen)}
        />
      </button>

      {open && menuPosition && createPortal(
        <ul ref={listRef} className={styles.list} style={menuPosition}>
          {options.map((option) => (
            <li key={option.value}>
              <button
                type="button"
                className={classNames(styles.option, option.value === value && styles.optionActive)}
                onClick={() => {
                  onChange(option.value);
                  setOpen(false);
                }}
              >
                {option.image && (
                  <span className={styles.avatar}>
                    <Image src={option.image} alt="" fill sizes="40px" />
                  </span>
                )}

                <span className={styles.text}>
                  <span className={styles.title}>{option.label}</span>
                  {option.hint && <span className={styles.hint}>{option.hint}</span>}
                </span>
              </button>
            </li>
          ))}
        </ul>,
        document.body,
      )}
    </div>
  );
};

export default SelectField;
