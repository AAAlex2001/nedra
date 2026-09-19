import type { ExpertApplicationRecord, ExpertCatalog } from "@/entities/expert";
import { ApplicationsList } from "@/features/experts-admin";
import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type AdminExpertsProps = {
  items: ExpertApplicationRecord[];
  catalog: ExpertCatalog | null;
  error: string | null;
  basePath: string;
};

const AdminExperts = ({ items, catalog, error, basePath }: AdminExpertsProps) => (
  <section className={styles.section}>
    <div className={styles.heading}>
      <h1 className={styles.title}>Заявки экспертов</h1>
      <AccentLine width={30} />
      <p className={styles.subtitle}>
        Проверьте удостоверения и одобрите заявку: эксперт получит письмо и доступ
        в кабинет. При отклонении укажите причину.
      </p>
    </div>

    {error ? (
      <p className={styles.error}>{error}</p>
    ) : (
      <ApplicationsList initialItems={items} catalog={catalog} basePath={basePath} />
    )}
  </section>
);

export default AdminExperts;
