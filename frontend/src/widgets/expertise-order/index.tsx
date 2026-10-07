"use client";

import type { ExpertCatalog } from "@/entities/expert";
import { CustomerGate } from "@/features/auth";
import { ExpertiseForm } from "@/features/expertise-order";
import styles from "./style.module.scss";

type ExpertiseOrderProps = {
  catalog: ExpertCatalog | null;
};

const ExpertiseOrder = ({ catalog }: ExpertiseOrderProps) => {
  if (!catalog) {
    return <p className={styles.error}>Не удалось загрузить справочник. Обновите страницу.</p>;
  }

  return (
    <CustomerGate
      title="Чтобы отправить документацию, войдите как заказчик"
      text="Регистрация занимает минуту. После входа заявка уйдёт экспертам, аттестованным по вашей отрасли."
    >
      <ExpertiseForm catalog={catalog} />
    </CustomerGate>
  );
};

export default ExpertiseOrder;
