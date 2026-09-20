"use client";

import { INVOICE_STAGE_LABELS, invoicePdfUrl } from "@/entities/billing";
import { formatRequestDate } from "@/entities/request";
import { formatRub } from "@/shared/lib/money";
import Loader from "@/shared/ui/loader";
import { useInvoices } from "../../model/use-invoices";
import DocumentList from "../document-list";
import styles from "./style.module.scss";

const InvoicesTab = () => {
  const state = useInvoices();

  if (state.status === "loading") {
    return <Loader />;
  }

  if (state.status === "error") {
    return <p className={styles.error}>{state.message}</p>;
  }

  if (state.items.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyTitle}>Счетов пока нет</p>
        <p className={styles.emptyText}>
          Счёт появляется, когда вы выбираете оплату по безналичному расчёту на шаге
          оплаты в заявке. Перед этим заполните реквизиты организации в разделе «Мои данные».
        </p>
      </div>
    );
  }

  const items = state.items.map((invoice) => ({
    key: String(invoice.id),
    title: `Счёт № ${invoice.number}`,
    meta: `Заявка №${invoice.expertise_id} · ${INVOICE_STAGE_LABELS[invoice.stage]} · ${formatRequestDate(invoice.created_at)}`,
    amount: formatRub(invoice.amount),
    href: invoicePdfUrl(invoice.id),
    status: (
      <span className={invoice.paid_at ? styles.paid : styles.waiting}>
        {invoice.paid_at ? "Оплачен" : "Ждёт оплаты"}
      </span>
    ),
  }));

  return <DocumentList items={items} />;
};

export default InvoicesTab;
