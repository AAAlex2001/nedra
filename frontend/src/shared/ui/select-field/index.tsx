"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";
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
};

const SelectField = ({
  label,
  placeholder,
  options,
  value,
  onChange,
  required,
}: SelectFieldProps) => {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  const selected = options.find((option) => option.value === value);

  useEffect(() => {
    if (!open) return;

    const closeOnClickOutside = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };

    document.addEventListener("mousedown", closeOnClickOutside);

    return () => document.removeEventListener("mousedown", closeOnClickOutside);
  }, [open]);

  return (
    <div className={styles.field} ref={rootRef}>
      <span className={styles.label}>
        {label}
        {required && <span className={styles.required}> *</span>}
      </span>

      <button
        type="button"
        className={`${styles.control} ${open ? styles.controlOpen : ""}`}
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
          className={`${styles.chevron} ${open ? styles.chevronOpen : ""}`}
        />
      </button>

      {open && (
        <ul className={styles.list}>
          {options.map((option) => (
            <li key={option.value}>
              <button
                type="button"
                className={`${styles.option} ${
                  option.value === value ? styles.optionActive : ""
                }`}
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
        </ul>
      )}
    </div>
  );
};

export default SelectField;
