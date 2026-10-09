"use client";

import { useState } from "react";
import { AUDIT_FILES_ACCEPT } from "@/entities/expertise";
import Button from "@/shared/ui/button";
import FilesField from "@/shared/ui/files-field";
import TextField from "@/shared/ui/text-field";
import styles from "./style.module.scss";

const ACCEPT = ".pdf,.doc,.docx,.jpg,.jpeg,.png";

type RevisionFormProps = {
  audit: boolean;
  pending: boolean;
  onSubmit: (formData: FormData) => void;
};

const RevisionForm = ({ audit, pending, onSubmit }: RevisionFormProps) => {
  const [text, setText] = useState("");
  const [files, setFiles] = useState<File[]>([]);

  const canSubmit = files.length > 0 && !pending;

  const submit = () => {
    if (!canSubmit) return;

    const formData = new FormData();
    if (text.trim() !== "") formData.append("text", text.trim());
    for (const file of files) {
      formData.append("files", file);
    }

    onSubmit(formData);
  };

  return (
    <div className={styles.form}>
      <FilesField
        label={audit ? "Исправленные документы" : "Исправленная документация"}
        required
        files={files}
        accept={audit ? AUDIT_FILES_ACCEPT : ACCEPT}
        hint={
          audit
            ? "PDF, файлы электронной подписи, фото или видео. Аудитор проверит документы повторно."
            : "Приложите документацию с внесёнными изменениями. Эксперт проверит её повторно."
        }
        onAdd={(chosen) => setFiles([...files, ...chosen])}
        onRemove={(index) => setFiles(files.filter((file, position) => position !== index))}
      />

      <TextField
        label={audit ? "Комментарий аудитору" : "Комментарий эксперту"}
        multiline
        rows={4}
        placeholder="Что именно исправили: раздел, суть правки"
        maxLength={4000}
        value={text}
        onChange={setText}
      />

      <Button
        className={styles.submit}
        disabled={!canSubmit}
        loading={pending}
        onClick={submit}
      >
        {audit ? "Отправить аудитору повторно" : "Повторно отправить на экспертизу"}
      </Button>
    </div>
  );
};

export default RevisionForm;
