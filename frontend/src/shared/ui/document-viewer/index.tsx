"use client";

import { useEffect } from "react";
import { createPortal } from "react-dom";
import { CloseIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

export type DocumentKind = "pdf" | "word" | "excel";

export type ViewedDocument = {
  title: string;
  href: string;
  kind: DocumentKind;
};

type DocumentViewerProps = {
  file: ViewedDocument;
  onClose: () => void;
};

const OFFICE_VIEWER = "https://view.officeapps.live.com/op/embed.aspx?src=";

const viewerSource = (file: ViewedDocument): string => {
  const absoluteUrl = new URL(file.href, window.location.origin).toString();

  if (file.kind === "pdf") return absoluteUrl;

  return `${OFFICE_VIEWER}${encodeURIComponent(absoluteUrl)}`;
};

const DocumentViewer = ({ file, onClose }: DocumentViewerProps) => {
  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };

    document.addEventListener("keydown", closeOnEscape);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", closeOnEscape);
      document.body.style.overflow = previousOverflow;
    };
  }, [onClose]);

  return createPortal(
    <div className={styles.overlay} role="dialog" aria-modal="true" aria-label={file.title}>
      <div className={styles.window}>
        <div className={styles.head}>
          <span className={styles.title}>{file.title}</span>

          <div className={styles.actions}>
            <a className={styles.action} href={file.href} download>
              Скачать
            </a>
            <a className={styles.action} href={file.href} target="_blank" rel="noopener noreferrer">
              В новой вкладке
            </a>
            <button type="button" className={styles.close} aria-label="Закрыть" onClick={onClose}>
              <CloseIcon className={styles.closeIcon} />
            </button>
          </div>
        </div>

        <iframe className={styles.frame} src={viewerSource(file)} title={file.title} />
      </div>
    </div>,
    document.body,
  );
};

export default DocumentViewer;
