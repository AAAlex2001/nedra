"use client";

import classNames from "classnames";
import { useEffect, useRef, useState } from "react";
import { CheckIcon, ChevronIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

export type MultiSelectOption = {
  value: string;
  label: string;
};

type MultiSelectFieldProps = {
  label?: string;
  placeholder: string;
  options: MultiSelectOption[];
  value: string[];
  onChange: (value: string[]) => void;
};

const MultiSelectField = ({ label, placeholder, options, value, onChange }: MultiSelectFieldProps) => {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    const closeOnClickOutside = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };

    document.addEventListener("mousedown", closeOnClickOutside);

    return () => document.removeEventListener("mousedown", closeOnClickOutside);
  }, [open]);

  const toggle = (option: string) => {
    const next = value.includes(option)
      ? value.filter((item) => item !== option)
      : [...value, option];

    onChange(next);
  };

  const selected = options.filter((option) => value.includes(option.value));
  const summary = selected.map((option) => option.label).join(", ");

  return (
    <div className={styles.field} ref={rootRef}>
      {label && <span className={styles.label}>{label}</span>}

      <button
        type="button"
        className={classNames(styles.control, open && styles.controlOpen)}
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        <span className={summary ? styles.summary : styles.placeholder}>
          {summary || placeholder}
        </span>
        <ChevronIcon className={classNames(styles.chevron, open && styles.chevronOpen)} />
      </button>

      {open && (
        <ul className={styles.list} role="listbox" aria-multiselectable="true">
          {options.map((option) => {
            const checked = value.includes(option.value);

            return (
              <li key={option.value}>
                <button
                  type="button"
                  role="option"
                  aria-selected={checked}
                  className={classNames(styles.option, checked && styles.optionActive)}
                  onClick={() => toggle(option.value)}
                >
                  <span className={classNames(styles.box, checked && styles.boxChecked)}>
                    {checked && <CheckIcon className={styles.check} />}
                  </span>
                  <span className={styles.optionLabel}>{option.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

export default MultiSelectField;
