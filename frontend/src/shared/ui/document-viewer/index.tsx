"use client";

import { useEffect, useRef } from "react";
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
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const previousFocus = document.activeElement;
    const dialog = dialogRef.current;
    dialog?.showModal();
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      dialog?.close();
      document.body.style.overflow = previousOverflow;
      if (previousFocus instanceof HTMLElement) previousFocus.focus();
    };
  }, []);

  return createPortal(
    <dialog
      ref={dialogRef}
      className={styles.overlay}
      aria-label={file.title}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div className={styles.window}>
        <div className={styles.head}>
          <span className={styles.title}>{file.title}</span>

          <div className={styles.actions}>
            <a className={styles.action} href={file.href} download>
              Скачать
            </a>
            <button type="button" className={styles.close} aria-label="Закрыть" autoFocus onClick={onClose}>
              <CloseIcon className={styles.closeIcon} />
            </button>
          </div>
        </div>

        <iframe className={styles.frame} src={viewerSource(file)} title={file.title} />
      </div>
    </dialog>,
    document.body,
  );
};

export default DocumentViewer;
