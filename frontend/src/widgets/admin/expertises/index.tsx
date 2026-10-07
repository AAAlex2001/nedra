import type { ExpertCatalog } from "@/entities/expert";
import {
  ExpertisesList,
  type ExpertiseAdminRecord,
  type ExpertOption,
} from "@/features/expertises-admin";
import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type AdminExpertisesProps = {
  items: ExpertiseAdminRecord[];
  catalog: ExpertCatalog | null;
  experts: ExpertOption[];
  error: string | null;
  basePath: string;
};

const AdminExpertises = ({ items, catalog, experts, error, basePath }: AdminExpertisesProps) => (
  <section className={styles.section}>
    <div className={styles.heading}>
      <h1 className={styles.title}>Заявки на экспертизу</h1>
      <AccentLine width={30} />
      <p className={styles.subtitle}>
        Заявки с «Блиц-эксперта». Можно поправить статус и стоимость, назначить эксперта
        или удалить заявку вместе с файлами.
      </p>
    </div>

    {error ? (
      <p className={styles.error}>{error}</p>
    ) : (
      <ExpertisesList
        initialItems={items}
        catalog={catalog}
        experts={experts}
        basePath={basePath}
      />
    )}
  </section>
);

export default AdminExpertises;
