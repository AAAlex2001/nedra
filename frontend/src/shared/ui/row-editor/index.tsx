import type { ReactNode } from "react";
import Button from "@/shared/ui/button";
import styles from "./style.module.scss";

type RowEditorProps = {
  pending: boolean;
  error: string | null;
  saveText?: string;
  saveDisabled?: boolean;
  onSave: () => void;
  onCancel: () => void;
  children: ReactNode;
};

const RowEditor = ({
  pending,
  error,
  saveText = "Сохранить",
  saveDisabled = false,
  onSave,
  onCancel,
  children,
}: RowEditorProps) => (
  <div className={styles.editor}>
    {children}

    {error && <p className={styles.error}>{error}</p>}

    <div className={styles.buttons}>
      <button type="button" className={styles.cancel} disabled={pending} onClick={onCancel}>
        Отмена
      </button>
      <Button className={styles.save} loading={pending} disabled={saveDisabled} onClick={onSave}>
        {saveText}
      </Button>
    </div>
  </div>
);

export default RowEditor;
