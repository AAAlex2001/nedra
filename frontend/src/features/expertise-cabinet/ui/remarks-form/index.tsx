"use client";

import { useState } from "react";
import Button from "@/shared/ui/button";
import FilesField from "@/shared/ui/files-field";
import TextField from "@/shared/ui/text-field";
import styles from "./style.module.scss";

const ACCEPT = ".pdf,.doc,.docx";

type RemarksFormProps = {
  pending: boolean;
  onSubmit: (formData: FormData) => void;
  onCancel: () => void;
};

const RemarksForm = ({ pending, onSubmit, onCancel }: RemarksFormProps) => {
  const [text, setText] = useState("");
  const [files, setFiles] = useState<File[]>([]);

  const canSubmit = (text.trim() !== "" || files.length > 0) && !pending;

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
      <p className={styles.title}>
        Рекомендации по приведению объекта экспертизы в соответствие с требованиями промышленной
        безопасности
      </p>

      <TextField
        label="Замечания"
        multiline
        rows={6}
        placeholder="Что нужно исправить в документации: раздел, пункт правил, суть замечания"
        maxLength={4000}
        value={text}
        onChange={setText}
      />

      <FilesField
        label="Файл с замечаниями"
        files={files}
        accept={ACCEPT}
        hint="PDF или Word, если замечания оформлены отдельным документом. Можно прислать только текст, только файл или и то и другое."
        onAdd={(chosen) => setFiles([...files, ...chosen])}
        onRemove={(index) => setFiles(files.filter((file, position) => position !== index))}
      />

      <div className={styles.buttons}>
        <button type="button" className={styles.cancel} disabled={pending} onClick={onCancel}>
          Отмена
        </button>
        <Button disabled={!canSubmit} loading={pending} onClick={submit}>
          Отправить замечания
        </Button>
      </div>
    </div>
  );
};

export default RemarksForm;
