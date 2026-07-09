import { DocumentIcon } from "@/shared/ui/icons";
import type { FieldItem } from "../../data";
import styles from "./style.module.scss";

type FieldsLicensesProps = {
  item: FieldItem;
};

const FieldsLicenses = ({ item }: FieldsLicensesProps) => {
  if (!item.licenseColumns?.length) {
    return null;
  }

  return (
    <div className={styles.card}>
      <h4 className={styles.title}>
        {item.licensesTitle ?? "Разрешительные документы"}
      </h4>

      <div className={styles.columns}>
        {item.licenseColumns.map((column) => (
          <div key={column.file.title} className={styles.column}>
            <div className={styles.note}>
              <span className={styles.dot} aria-hidden="true" />
              <span>{column.text}</span>
            </div>
            <a href={column.file.href} className={styles.file}>
              <DocumentIcon />
              <span className={styles.fileText}>
                <span className={styles.fileTitle}>{column.file.title}</span>
                <span className={styles.fileMeta}>{column.file.meta}</span>
              </span>
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FieldsLicenses;
