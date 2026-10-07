"use client";

import type { AuditChecklistItem } from "@/entities/expertise";
import { CustomerGate } from "@/features/auth";
import { AuditForm } from "@/features/expertise-order";
import styles from "./style.module.scss";

type AuditOrderProps = {
  checklist: AuditChecklistItem[];
};

const AuditOrder = ({ checklist }: AuditOrderProps) => {
  if (checklist.length === 0) {
    return <p className={styles.error}>Не удалось загрузить перечень документов. Обновите страницу.</p>;
  }

  return (
    <CustomerGate
      title="Чтобы загрузить документы на аудит, войдите как заказчик"
      text="Регистрация занимает минуту. После входа загрузите документы по перечню — заявку сразу увидят аудиторы."
    >
      <AuditForm checklist={checklist} />
    </CustomerGate>
  );
};

export default AuditOrder;
