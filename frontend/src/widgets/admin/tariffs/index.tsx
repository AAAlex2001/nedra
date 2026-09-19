import type { ExpertCatalog } from "@/entities/expert";
import type { Tariff } from "@/entities/tariff";
import { TariffGrid } from "@/features/tariffs-admin";
import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type AdminTariffsProps = {
  catalog: ExpertCatalog | null;
  tariffs: Tariff[];
  error: string | null;
  basePath: string;
};

const AdminTariffs = ({ catalog, tariffs, error, basePath }: AdminTariffsProps) => (
  <section className={styles.section}>
    <div className={styles.heading}>
      <h1 className={styles.title}>Тарифы на экспертизу</h1>
      <AccentLine width={30} />
      <p className={styles.subtitle}>
        Стоимость по парам «область аттестации × объект экспертизы». Эти цены видят
        заказчики на странице «Блиц-эксперт», и они же подставляются в договор.
      </p>
    </div>

    {error || !catalog ? (
      <p className={styles.error}>{error ?? "Не удалось загрузить справочник"}</p>
    ) : (
      <TariffGrid catalog={catalog} initialTariffs={tariffs} basePath={basePath} />
    )}
  </section>
);

export default AdminTariffs;
