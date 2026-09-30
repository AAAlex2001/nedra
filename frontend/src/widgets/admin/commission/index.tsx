import type { CommissionApplicationRecord } from "@/entities/commission";
import type { ExpertCatalog } from "@/entities/expert";
import { CommissionApplicationsList } from "@/features/commission-admin";
import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type AdminCommissionProps = {
  items: CommissionApplicationRecord[];
  catalog: ExpertCatalog | null;
  error: string | null;
  basePath: string;
};

const AdminCommission = ({ items, catalog, error, basePath }: AdminCommissionProps) => (
  <section className={styles.section}>
    <div className={styles.heading}>
      <h1 className={styles.title}>Конкурсная комиссия</h1>
      <AccentLine width={30} />
      <p className={styles.subtitle}>
        Заявки кандидатов в эксперты из всплывающего окна на сайте.
      </p>
    </div>

    {error ? (
      <p className={styles.error}>{error}</p>
    ) : (
      <CommissionApplicationsList initialItems={items} catalog={catalog} basePath={basePath} />
    )}
  </section>
);

export default AdminCommission;
