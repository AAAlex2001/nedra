"use client";

import classNames from "classnames";
import Link from "next/link";
import { useEffect, useId, useRef, useState } from "react";
import { CheckIcon, ChevronIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type FilterOption = {
  value: string;
  label: string;
  href: string;
};

type ListFilterProps = {
  label: string;
  options: FilterOption[];
  value: string;
  highlighted?: boolean;
};

const ListFilter = ({ label, options, value, highlighted }: ListFilterProps) => {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const listId = useId();
  const selected = options.find((option) => option.value === value) ?? options[0];

  useEffect(() => {
    if (!open) return;

    const closeOnOutsideClick = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };

    document.addEventListener("pointerdown", closeOnOutsideClick);
    return () => document.removeEventListener("pointerdown", closeOnOutsideClick);
  }, [open]);

  return (
    <div
      ref={rootRef}
      className={styles.root}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);
      }}
      onKeyDown={(event) => {
        if (event.key === "Escape" && open) {
          event.stopPropagation();
          setOpen(false);
          buttonRef.current?.focus();
        }
      }}
    >
      <button
        ref={buttonRef}
        type="button"
        className={classNames(styles.control, open && styles.controlOpen, highlighted && styles.controlActive)}
        aria-label={`${label}: ${selected.label}`}
        aria-expanded={open}
        aria-controls={listId}
        onClick={() => setOpen(!open)}
      >
        <span className={styles.controlText}>{selected.label}</span>
        <ChevronIcon className={classNames(styles.chevron, open && styles.chevronOpen)} />
      </button>

      {open && (
        <ul id={listId} className={styles.list} aria-label={label}>
          {options.map((option) => (
            <li key={option.value}>
              <Link
                href={option.href}
                scroll={false}
                aria-current={option.value === value ? "true" : undefined}
                className={classNames(styles.option, option.value === value && styles.optionActive)}
                onClick={() => setOpen(false)}
              >
                <span>{option.label}</span>
                {option.value === value && <CheckIcon className={styles.check} />}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ListFilter;
