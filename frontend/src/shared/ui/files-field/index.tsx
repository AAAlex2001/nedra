"use client";

import { useId } from "react";
import styles from "./style.module.scss";

type FilesFieldProps = {
  label: string;
  files: File[];
  onAdd: (files: File[]) => void;
  onRemove: (index: number) => void;
  accept?: string;
  hint?: string;
  required?: boolean;
};

const formatSize = (bytes: number): string => {
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} КБ`;

  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
};

const FilesField = ({ label, files, onAdd, onRemove, accept, hint, required }: FilesFieldProps) => {
  const inputId = useId();

  return (
    <div className={styles.field}>
      <span className={styles.label}>
        {label}
        {required && <span className={styles.required}> *</span>}
      </span>

      <label htmlFor={inputId} className={styles.dropzone}>
        <span className={styles.button}>Выбрать файлы</span>
        <span className={styles.text}>или перетащите их сюда</span>
      </label>

      <input
        id={inputId}
        className={styles.input}
        type="file"
        multiple
        accept={accept}
        onChange={(event) => {
          const chosen = Array.from(event.target.files ?? []);
          onAdd(chosen);
          event.target.value = "";
        }}
      />

      {files.length > 0 && (
        <ul className={styles.list}>
          {files.map((file, index) => (
            <li key={`${file.name}-${index}`} className={styles.item}>
              <span className={styles.name}>{file.name}</span>
              <span className={styles.size}>{formatSize(file.size)}</span>
              <button
                type="button"
                className={styles.remove}
                aria-label={`Убрать ${file.name}`}
                onClick={() => onRemove(index)}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}

      {hint && <span className={styles.hint}>{hint}</span>}
    </div>
  );
};

export default FilesField;
