"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import type { Tag } from "@/entities/article";
import { CheckIcon, ChevronIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type TagFilterProps = {
  basePath: string;
  tags: Tag[];
  activeTag: string | null;
};

const ALL_LABEL = "Все направления";

const TagFilter = ({ basePath, tags, activeTag }: TagFilterProps) => {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  const selected = tags.find((tag) => tag.slug === activeTag);
  const title = selected ? selected.title : ALL_LABEL;

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
    <div className={styles.root} ref={rootRef}>
      <button
        type="button"
        className={`${styles.control} ${open ? styles.controlOpen : ""} ${selected ? styles.controlActive : ""}`}
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        <span className={styles.controlText}>{title}</span>
        <ChevronIcon className={`${styles.chevron} ${open ? styles.chevronOpen : ""}`} />
      </button>

      {open && (
        <ul className={styles.list} role="listbox" aria-label="Направления">
          <li>
            <Link
              href={basePath}
              className={`${styles.option} ${selected ? "" : styles.optionActive}`}
              onClick={() => setOpen(false)}
            >
              <span>{ALL_LABEL}</span>
              {!selected && <CheckIcon className={styles.check} />}
            </Link>
          </li>

          {tags.map((tag) => {
            const active = tag.slug === activeTag;

            return (
              <li key={tag.slug}>
                <Link
                  href={`${basePath}?tag=${tag.slug}`}
                  className={`${styles.option} ${active ? styles.optionActive : ""}`}
                  onClick={() => setOpen(false)}
                >
                  <span>{tag.title}</span>
                  {active && <CheckIcon className={styles.check} />}
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

export default TagFilter;
