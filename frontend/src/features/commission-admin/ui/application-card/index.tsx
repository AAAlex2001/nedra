"use client";

import type { CommissionApplicationRecord } from "@/entities/commission";
import { areaTitle, formatCategory, objectLabel, type ExpertCatalog } from "@/entities/expert";
import { formatRequestDate } from "@/entities/request";
import Spinner from "@/shared/ui/spinner";
import styles from "./style.module.scss";

type ApplicationCardProps = {
  application: CommissionApplicationRecord;
  catalog: ExpertCatalog | null;
  pending: boolean;
  onDelete: (id: number) => void;
};

const ApplicationCard = ({ application, catalog, pending, onDelete }: ApplicationCardProps) => {
  const handleDelete = () => {
    if (window.confirm(`Удалить заявку №${application.id}?`)) {
      onDelete(application.id);
    }
  };

  return (
    <article className={`${styles.card} ${pending ? styles.cardPending : ""}`}>
      <header className={styles.head}>
        <div className={styles.headMain}>
          <span className={styles.id}>№{application.id}</span>
          <time className={styles.date} dateTime={application.created_at}>
            {formatRequestDate(application.created_at)}
          </time>
        </div>

        <button type="button" className={styles.delete} disabled={pending} onClick={handleDelete}>
          {pending ? <Spinner size={14} /> : "Удалить"}
        </button>
      </header>

      <p className={styles.name}>{application.full_name}</p>

      <ul className={styles.list}>
        {application.attestations.map((item) => (
          <li key={`${item.area_code}-${item.object_code}-${item.category}`} className={styles.item}>
            <span className={styles.code}>{item.area_code}</span>
            <span className={styles.object}>
              {catalog ? objectLabel(catalog, item.object_code) : item.object_code}
            </span>
            <span className={styles.meta}>{formatCategory(item.category)}</span>
            {catalog && <span className={styles.area}>{areaTitle(catalog, item.area_code)}</span>}
          </li>
        ))}
      </ul>
    </article>
  );
};

export default ApplicationCard;
