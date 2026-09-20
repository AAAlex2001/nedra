"use client";

import { actPdfUrl } from "@/entities/billing";
import { formatRequestDate } from "@/entities/request";
import { formatRub } from "@/shared/lib/money";
import Loader from "@/shared/ui/loader";
import { useActs } from "../../model/use-acts";
import DocumentList from "../document-list";
import styles from "./style.module.scss";

const ActsTab = () => {
  const state = useActs();

  if (state.status === "loading") {
    return <Loader />;
  }

  if (state.status === "error") {
    return <p className={styles.error}>{state.message}</p>;
  }

  if (state.items.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyTitle}>Актов пока нет</p>
        <p className={styles.emptyText}>
          Акт выполненных работ формируется, когда вы принимаете работу по заявке.
          Для печати нужны реквизиты организации из раздела «Мои данные».
        </p>
      </div>
    );
  }

  const items = state.items.map((act) => ({
    key: String(act.expertise_id),
    title: `Акт № ${act.number}`,
    meta: `Заявка №${act.expertise_id} · ${act.subject} · ${formatRequestDate(act.signed_at)}`,
    amount: formatRub(act.amount),
    href: actPdfUrl(act.expertise_id),
  }));

  return <DocumentList items={items} />;
};

export default ActsTab;
