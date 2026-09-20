"use client";

import { useState } from "react";
import { EXPERTISE_RESULT_LABELS, type ExpertiseResult } from "@/entities/expertise";
import Button from "@/shared/ui/button";
import Chip from "@/shared/ui/chip";
import FilesField from "@/shared/ui/files-field";
import styles from "./style.module.scss";

const RESULTS: ExpertiseResult[] = ["positive", "negative", "remarks"];
const ACCEPT = ".pdf,.doc,.docx,.sig,.p7s";

type ConclusionFormProps = {
  pending: boolean;
  onSubmit: (formData: FormData) => void;
};

const ConclusionForm = ({ pending, onSubmit }: ConclusionFormProps) => {
  const [result, setResult] = useState<ExpertiseResult | null>(null);
  const [files, setFiles] = useState<File[]>([]);

  const canSubmit = result !== null && files.length > 0 && !pending;

  const submit = () => {
    if (!canSubmit || result === null) return;

    const formData = new FormData();
    formData.append("result", result);
    for (const file of files) {
      formData.append("files", file);
    }

    onSubmit(formData);
  };

  return (
    <div className={styles.form}>
      <div className={styles.group}>
        <span className={styles.label}>Исход экспертизы</span>
        <div className={styles.row} role="group" aria-label="Исход экспертизы">
          {RESULTS.map((item) => (
            <Chip
              key={item}
              active={result === item}
              className={styles.rowChip}
              onClick={() => setResult(item)}
            >
              {EXPERTISE_RESULT_LABELS[item]}
            </Chip>
          ))}
        </div>
      </div>

      <FilesField
        label="Заключение"
        required
        files={files}
        accept={ACCEPT}
        hint="Подпишите заключение ЭЦП и приложите подписанный PDF. Если подпись отсоединённая, добавьте файл .sig или .p7s."
        onAdd={(chosen) => setFiles([...files, ...chosen])}
        onRemove={(index) => setFiles(files.filter((file, position) => position !== index))}
      />

      <Button className={styles.submit} disabled={!canSubmit} loading={pending} onClick={submit}>
        Отправить заказчику
      </Button>
    </div>
  );
};

export default ConclusionForm;
