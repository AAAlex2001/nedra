"use client";

import { useState } from "react";
import type { ArticleDocument } from "@/entities/article";
import DocumentViewer, { type ViewedDocument } from "@/shared/ui/document-viewer";
import styles from "./style.module.scss";

type ArticleDocumentsProps = {
  documents: ArticleDocument[];
};

const extensionOf = (url: string): string => {
  const dotIndex = url.lastIndexOf(".");

  return url.slice(dotIndex + 1).toUpperCase();
};

const FileIcon = () => (
  <svg
    className={styles.icon}
    width="22"
    height="22"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <path d="M7 3h7l5 5v13H7V3Z" />
    <path d="M14 3v5h5" />
  </svg>
);

const ArticleDocuments = ({ documents }: ArticleDocumentsProps) => {
  const [file, setFile] = useState<ViewedDocument | null>(null);

  return (
    <>
      <ul className={styles.list}>
        {documents.map((item) => (
          <li key={item.url} className={styles.item}>
            <span className={styles.title}>{item.title}</span>
            <button
              type="button"
              className={styles.tile}
              aria-label={`Открыть документ «${item.title}»`}
              onClick={() => setFile({ title: item.title, href: item.url, kind: item.kind })}
            >
              <FileIcon />
              <span className={styles.extension}>{extensionOf(item.url)}</span>
            </button>
          </li>
        ))}
      </ul>

      {file && <DocumentViewer file={file} onClose={() => setFile(null)} />}
    </>
  );
};

export default ArticleDocuments;
