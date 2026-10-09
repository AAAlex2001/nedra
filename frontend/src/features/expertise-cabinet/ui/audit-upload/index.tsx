"use client";

import { useState } from "react";
import { AuditChecklist, type AuditFile } from "@/entities/expertise";
import Button from "@/shared/ui/button";
import { useAuditChecklist } from "../../model/use-audit-checklist";
import styles from "./style.module.scss";

type AuditUploadProps = {
  pending: boolean;
  onUpload: (files: AuditFile[]) => Promise<boolean>;
};

const NOTE =
  "Загрузите имеющиеся документы. Аудитор проанализирует комплектность и направит запрос на недостающие сведения. Принимаются PDF, файлы электронной подписи, фото и видео.";

const AuditUpload = ({ pending, onUpload }: AuditUploadProps) => {
  const checklist = useAuditChecklist();
  const [files, setFiles] = useState<AuditFile[]>([]);

  const add = (item: number, chosen: File[]) =>
    setFiles([...files, ...chosen.map((file) => ({ item, file }))]);

  const upload = async () => {
    const uploaded = await onUpload(files);
    if (uploaded) setFiles([]);
  };

  if (checklist.length === 0) return null;

  return (
    <div className={styles.form}>
      <AuditChecklist
        checklist={checklist}
        files={files}
        note={NOTE}
        onAdd={add}
        onRemove={(target) => setFiles(files.filter((entry) => entry !== target))}
      />

      <Button
        className={styles.submit}
        disabled={files.length === 0}
        loading={pending}
        onClick={() => void upload()}
      >
        Загрузить документы
      </Button>
    </div>
  );
};

export default AuditUpload;
