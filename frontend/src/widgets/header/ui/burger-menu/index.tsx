"use client";

import Link from "next/link";
import { useEffect } from "react";
import type { HeaderNavItem } from "../../data";
import styles from "./style.module.scss";

type BurgerMenuProps = {
  open: boolean;
  nav: HeaderNavItem[];
  onClose: () => void;
};

const BurgerMenu = ({ open, nav, onClose }: BurgerMenuProps) => {
  useEffect(() => {
    if (!open) return;

    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };

    document.addEventListener("keydown", onKey);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = previousOverflow;
    };
  }, [open, onClose]);

  return (
    <div
      className={`${styles.root} ${open ? styles.open : ""}`}
      aria-hidden={!open}
    >
      <div className={styles.overlay} onClick={onClose} />

      <nav className={styles.panel} aria-label="Меню">
        <div className={styles.inner}>
          {nav.map((item) => (
            <Link
              key={item.label}
              className={styles.navLink}
              href={item.href}
              onClick={onClose}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </nav>
    </div>
  );
};

export default BurgerMenu;
