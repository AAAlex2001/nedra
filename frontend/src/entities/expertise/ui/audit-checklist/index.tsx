"use client";

import classNames from "classnames";
import { CheckIcon, CloseIcon } from "@/shared/ui/icons";
import { AUDIT_FILES_ACCEPT, type AuditChecklistItem, type AuditFile } from "../../model/audit";
import styles from "./style.module.scss";

type AuditChecklistProps = {
  checklist: AuditChecklistItem[];
  files: AuditFile[];
  note: string;
  onAdd: (item: number, files: File[]) => void;
  onRemove: (target: AuditFile) => void;
};

const AuditChecklist = ({ checklist, files, note, onAdd, onRemove }: AuditChecklistProps) => {
  const covered = new Set(files.map((entry) => entry.item)).size;

  return (
    <div className={styles.root}>
      <div className={styles.head}>
        <span className={styles.label}>Документы по перечню</span>
        <span className={styles.counter}>
          Загружено по {covered} из {checklist.length} пунктов
        </span>
      </div>
      <p className={styles.note}>{note}</p>

      <ol className={styles.list}>
        {checklist.map((item) => {
          const attached = files.filter((entry) => entry.item === item.number);
          const done = attached.length > 0;

          return (
            <li key={item.number} className={classNames(styles.item, done && styles.itemDone)}>
              <span className={styles.number}>
                {done ? <CheckIcon className={styles.doneIcon} /> : item.number}
              </span>

              <div className={styles.body}>
                <p className={styles.title}>{item.title}</p>

                {attached.length > 0 && (
                  <ul className={styles.files}>
                    {attached.map((entry) => (
                      <li key={`${entry.file.name}-${entry.file.size}-${entry.file.lastModified}`} className={styles.file}>
                        <span className={styles.fileName}>{entry.file.name}</span>
                        <button
                          type="button"
                          className={styles.remove}
                          aria-label={`Удалить ${entry.file.name}`}
                          onClick={() => onRemove(entry)}
                        >
                          <CloseIcon className={styles.removeIcon} />
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <label className={styles.attach}>
                <input
                  className={styles.input}
                  type="file"
                  multiple
                  accept={AUDIT_FILES_ACCEPT}
                  onChange={(event) => {
                    const chosen = Array.from(event.target.files ?? []);
                    if (chosen.length > 0) onAdd(item.number, chosen);
                    event.target.value = "";
                  }}
                />
                {done ? "Ещё файл" : "Прикрепить"}
              </label>
            </li>
          );
        })}
      </ol>
    </div>
  );
};

export default AuditChecklist;
