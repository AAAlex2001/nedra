"use client";

import { useId } from "react";
import styles from "./style.module.scss";

type FileFieldProps = {
  label: string;
  file: File | null;
  onChange: (file: File | null) => void;
  accept?: string;
  hint?: string;
};

const FileField = ({ label, file, onChange, accept, hint }: FileFieldProps) => {
  const inputId = useId();

  return (
    <div className={styles.field}>
      <span className={styles.label}>{label}</span>

      <div className={styles.control}>
        <label htmlFor={inputId} className={styles.button}>
          Выбрать файл
        </label>
        <span className={styles.name}>{file ? file.name : "Файл не выбран"}</span>
        {file && (
          <button type="button" className={styles.clear} onClick={() => onChange(null)}>
            Убрать
          </button>
        )}
      </div>

      <input
        id={inputId}
        className={styles.input}
        type="file"
        accept={accept}
        onChange={(event) => {
          const chosen = event.target.files?.[0] ?? null;
          onChange(chosen);
          event.target.value = "";
        }}
      />

      {hint && <span className={styles.hint}>{hint}</span>}
    </div>
  );
};

export default FileField;
