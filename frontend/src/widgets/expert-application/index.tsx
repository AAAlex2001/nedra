import type { ExpertCatalog } from "@/entities/expert";
import { ExpertApplicationForm } from "@/features/expert-application";
import styles from "./style.module.scss";

type ExpertApplicationSectionProps = {
  catalog: ExpertCatalog | null;
};

const ExpertApplicationSection = ({ catalog }: ExpertApplicationSectionProps) => {
  if (!catalog) {
    return (
      <p className={styles.error}>
        Не удалось загрузить справочник аттестации. Обновите страницу или попробуйте позже.
      </p>
    );
  }

  return (
    <section className={styles.section}>
      <p className={styles.intro}>
        Эксперты промышленной безопасности работают на платформе после проверки
        удостоверений. Заполните заявку: мы сверим области аттестации с реестром
        и заведём аккаунт эксперта с доступом в личный кабинет.
      </p>

      <ExpertApplicationForm catalog={catalog} />
    </section>
  );
};

export default ExpertApplicationSection;
