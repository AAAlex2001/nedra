"use client";

import Link from "next/link";
import type { ExpertCatalog } from "@/entities/expert";
import { useSession } from "@/entities/user";
import { ExpertApplicationForm } from "@/features/expert-application";
import styles from "./style.module.scss";

type ExpertApplicationSectionProps = {
  catalog: ExpertCatalog | null;
};

const ExpertApplicationSection = ({ catalog }: ExpertApplicationSectionProps) => {
  const session = useSession();
  const account = session.user;

  if (!catalog) {
    return (
      <p className={styles.error}>
        Не удалось загрузить справочник аттестации. Обновите страницу или попробуйте позже.
      </p>
    );
  }

  if (account && account.is_expert) {
    return (
      <section className={styles.section}>
        <p className={styles.intro}>
          У вашего аккаунта уже есть профиль эксперта. Переключить роль можно в{" "}
          <Link href="/kabinet" className={styles.link}>
            личном кабинете
          </Link>
          .
        </p>
      </section>
    );
  }

  return (
    <section className={styles.section}>
      <p className={styles.intro}>
        Эксперты промышленной безопасности работают на платформе после проверки
        удостоверений. Заполните заявку: мы сверим области аттестации с реестром
        и откроем доступ в личный кабинет.
      </p>

      <ExpertApplicationForm catalog={catalog} account={account} />
    </section>
  );
};

export default ExpertApplicationSection;
