"use client";

import Image from "next/image";
import { useEffect, useId, useRef, useState } from "react";
import { ChevronIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

export type SelectOption = {
  id: string;
  title: string;
  subtitle?: string;
  image?: string;
};

type SelectProps = {
  label: string;
  placeholder: string;
  options: SelectOption[];
  value: string | null;
  onChange: (id: string) => void;
  required?: boolean;
  invalid?: boolean;
};

const Select = ({
  label,
  placeholder,
  options,
  value,
  onChange,
  required,
  invalid,
}: SelectProps) => {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const listId = useId();

  const selected = options.find((option) => option.id === value) ?? null;

  useEffect(() => {
    if (!open) return;

    const onPointerDown = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);

    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  return (
    <div className={styles.field} ref={rootRef}>
      <span className={styles.label}>
        {label}
        {required && <span className={styles.required}> *</span>}
      </span>

      <button
        type="button"
        className={`${styles.control} ${open ? styles.controlOpen : ""} ${
          invalid ? styles.controlInvalid : ""
        }`}
        onClick={() => setOpen((prev) => !prev)}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listId}
      >
        {selected?.image && (
          <span className={styles.avatar}>
            <Image src={selected.image} alt="" fill sizes="40px" />
          </span>
        )}

        <span className={styles.controlText}>
          {selected ? (
            <>
              <span className={styles.controlTitle}>{selected.title}</span>
              {selected.subtitle && (
                <span className={styles.controlSubtitle}>{selected.subtitle}</span>
              )}
            </>
          ) : (
            <span className={styles.placeholder}>{placeholder}</span>
          )}
        </span>

        <ChevronIcon
          className={`${styles.chevron} ${open ? styles.chevronOpen : ""}`}
        />
      </button>

      {open && (
        <ul className={styles.list} id={listId} role="listbox">
          {options.map((option) => (
            <li key={option.id}>
              <button
                type="button"
                role="option"
                aria-selected={option.id === value}
                className={`${styles.option} ${
                  option.id === value ? styles.optionActive : ""
                }`}
                onClick={() => {
                  onChange(option.id);
                  setOpen(false);
                }}
              >
                {option.image && (
                  <span className={styles.avatar}>
                    <Image src={option.image} alt="" fill sizes="40px" />
                  </span>
                )}

                <span className={styles.optionText}>
                  <span className={styles.optionTitle}>{option.title}</span>
                  {option.subtitle && (
                    <span className={styles.optionSubtitle}>{option.subtitle}</span>
                  )}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Select;
