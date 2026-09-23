"use client";

import { useEffect, type ReactNode } from "react";
import { CloseIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type ServicesModalProps = {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
};

const ServicesModal = ({ open, title, onClose, children }: ServicesModalProps) => {
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
    <div className={`${styles.root} ${open ? styles.open : ""}`} onClick={onClose}>
      <div
        className={styles.window}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(event) => event.stopPropagation()}
      >
        <div className={styles.head}>
          <h2 className={styles.title}>{title}</h2>
          <button type="button" className={styles.close} aria-label="Закрыть" onClick={onClose}>
            <CloseIcon className={styles.closeIcon} />
          </button>
        </div>

        <div className={styles.body}>{children}</div>
      </div>
    </div>
  );
};

export default ServicesModal;
