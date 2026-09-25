import { formatCategory, objectLabel, type ExpertCatalog } from "@/entities/expert";
import { formatDate } from "@/shared/lib/date";
import type { CertificateItem } from "../../model/types";
import styles from "./style.module.scss";

type CertificatesListProps = {
  catalog: ExpertCatalog;
  items: CertificateItem[];
  onRemove: (key: number) => void;
};

const CertificatesList = ({ catalog, items, onRemove }: CertificatesListProps) => {
  if (items.length === 0) {
    return <p className={styles.empty}>Добавьте хотя бы одно удостоверение.</p>;
  }

  return (
    <ul className={styles.list}>
      {items.map((item) => (
        <li key={item.key} className={styles.item}>
          <span className={styles.code}>{item.areaCode}</span>
          <span className={styles.object}>{objectLabel(catalog, item.objectCode)}</span>
          <span className={styles.meta}>
            {item.category !== null && formatCategory(item.category)} · до{" "}
            {formatDate(item.validUntil)}
          </span>
          <span className={styles.number}>№ {item.number}</span>
          <button
            type="button"
            className={styles.remove}
            aria-label="Удалить удостоверение"
            onClick={() => onRemove(item.key)}
          >
            ×
          </button>
        </li>
      ))}
    </ul>
  );
};

export default CertificatesList;
