import { DocumentIcon } from "@/shared/ui/icons";
import type { Licenses } from "../../data";
import styles from "./style.module.scss";

type LicenseCardProps = {
  licenses: Licenses;
};

const LicenseCard = ({ licenses }: LicenseCardProps) => {
  const columns = licenses.columns.filter((column) => column.text || column.doc);

  return (
    <div className={styles.card}>
      <h4 className={styles.title}>
        {licenses.title ?? "Разрешительные документы"}
      </h4>

      {licenses.note && <p className={styles.note}>{licenses.note}</p>}

      {columns.length > 0 && (
        <div className={styles.columns}>
          {columns.map((column, index) => (
            <div key={`${column.doc?.title ?? "license"}-${index}`} className={styles.column}>
              {column.text && (
                <div className={styles.colNote}>
                  <span className={styles.dot} aria-hidden="true" />
                  <span>{column.text}</span>
                </div>
              )}
              {column.doc &&
                (column.doc.href && column.doc.href !== "#" ? (
                  <a
                    href={column.doc.href}
                    className={styles.file}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <DocumentIcon />
                    <span className={styles.fileText}>
                      <span className={styles.fileTitle}>{column.doc.title}</span>
                      <span className={styles.fileMeta}>{column.doc.meta}</span>
                    </span>
                  </a>
                ) : (
                  <div className={styles.file}>
                    <DocumentIcon />
                    <span className={styles.fileText}>
                      <span className={styles.fileTitle}>{column.doc.title}</span>
                      <span className={styles.fileMeta}>{column.doc.meta}</span>
                    </span>
                  </div>
                ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LicenseCard;
