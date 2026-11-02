"use client";

import { useState } from "react";
import type { ArticleDocumentInput } from "@/entities/article";
import { uploadDocument } from "../api/admin-articles";

export const DOCUMENT_ACCEPT = ".pdf,.doc,.docx,.xls,.xlsx";

const titleFromFileName = (fileName: string): string => {
  const dotIndex = fileName.lastIndexOf(".");

  return dotIndex > 0 ? fileName.slice(0, dotIndex) : fileName;
};

export const useDocumentUploads = (
  basePath: string,
  onUploaded: (item: ArticleDocumentInput) => void,
) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upload = async (file: File) => {
    setUploading(true);
    setError(null);

    try {
      const { url } = await uploadDocument(basePath, file);
      onUploaded({ title: titleFromFileName(file.name), url });
    } catch (uploadError) {
      const message =
        uploadError instanceof Error ? uploadError.message : "Не удалось загрузить документ";
      setError(message);
    } finally {
      setUploading(false);
    }
  };

  return { uploading, error, upload };
};
