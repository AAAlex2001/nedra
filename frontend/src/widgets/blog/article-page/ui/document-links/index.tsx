"use client";

import { useEffect, useState } from "react";
import DocumentViewer, { type DocumentKind, type ViewedDocument } from "@/shared/ui/document-viewer";

const DOCUMENT_LINK = "[data-toc-content] a.document-link";

const toKind = (value: string | undefined): DocumentKind | null => {
  if (value === "pdf" || value === "word" || value === "excel") return value;

  return null;
};

const DocumentLinks = () => {
  const [file, setFile] = useState<ViewedDocument | null>(null);

  useEffect(() => {
    const openDocument = (event: MouseEvent) => {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey) return;

      const target = event.target as Element | null;
      const link = target?.closest(DOCUMENT_LINK);
      if (!(link instanceof HTMLAnchorElement)) return;

      const kind = toKind(link.dataset.kind);
      const href = link.getAttribute("href");
      if (!kind || !href) return;

      event.preventDefault();
      setFile({ title: link.textContent?.trim() || "Документ", href, kind });
    };

    document.addEventListener("click", openDocument);

    return () => document.removeEventListener("click", openDocument);
  }, []);

  if (!file) return null;

  return <DocumentViewer file={file} onClose={() => setFile(null)} />;
};

export default DocumentLinks;
