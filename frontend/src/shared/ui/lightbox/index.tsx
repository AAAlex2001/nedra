"use client";

import Image from "next/image";
import { useEffect } from "react";
import { createPortal } from "react-dom";
import styles from "./style.module.scss";

type LightboxProps = {
  src: string;
  alt?: string;
  onClose: () => void;
};

const Lightbox = ({ src, alt = "", onClose }: LightboxProps) => {
  useEffect(() => {
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
  }, [onClose]);

  return createPortal(
    <div
      className={styles.overlay}
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <button type="button" className={styles.close} aria-label="Закрыть" onClick={onClose}>
        <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M6 6L18 18M18 6L6 18"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      </button>

      <Image
        className={styles.image}
        src={src}
        alt={alt}
        width={1241}
        height={1755}
        sizes="100vw"
        quality={90}
        loading="eager"
        decoding="async"
        onClick={(event) => event.stopPropagation()}
        draggable={false}
      />
    </div>,
    document.body,
  );
};

export default Lightbox;
