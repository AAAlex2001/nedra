"use client";

import { useState } from "react";
import { uploadDocument } from "../api/admin-articles";

export type UploadedDocument = {
  title: string;
  url: string;
};

export const DOCUMENT_ACCEPT = ".pdf,.doc,.docx,.xls,.xlsx";

const titleFromFileName = (fileName: string): string => {
  const dotIndex = fileName.lastIndexOf(".");

  return dotIndex > 0 ? fileName.slice(0, dotIndex) : fileName;
};

const escapeHtml = (text: string): string =>
  text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");

export const documentSnippet = (item: UploadedDocument): string =>
  `\n<p><a href="${item.url}">${escapeHtml(item.title)}</a></p>\n`;

export const useDocumentUploads = (
  basePath: string,
  onUploaded: (item: UploadedDocument) => void,
) => {
  const [items, setItems] = useState<UploadedDocument[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upload = async (file: File) => {
    setUploading(true);
    setError(null);

    try {
      const { url } = await uploadDocument(basePath, file);
      const uploaded: UploadedDocument = { title: titleFromFileName(file.name), url };

      setItems([...items, uploaded]);
      onUploaded(uploaded);
    } catch (uploadError) {
      const message =
        uploadError instanceof Error ? uploadError.message : "Не удалось загрузить документ";
      setError(message);
    } finally {
      setUploading(false);
    }
  };

  return { items, uploading, error, upload };
};
