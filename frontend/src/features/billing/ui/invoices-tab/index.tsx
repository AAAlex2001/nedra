"use client";

import { INVOICE_STAGE_LABELS, invoicePdfUrl, type Invoice } from "@/entities/billing";
import { formatRequestDate } from "@/entities/request";
import { formatRub } from "@/shared/lib/money";
import Loader from "@/shared/ui/loader";
import { useInvoices } from "../../model/use-invoices";
import DocumentList from "../document-list";
import styles from "./style.module.scss";

const InvoicesTab = () => {
  const { state, pendingId, error, report } = useInvoices();

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
          оплаты в заявке. В счёт попадают реквизиты организации, указанные в заявке.
        </p>
      </div>
    );
  }

  const statusOf = (invoice: Invoice) => {
    if (invoice.paid_at !== null) {
      return <span className={styles.paid}>Оплачен</span>;
    }

    if (invoice.reported_at !== null) {
      return <span className={styles.reported}>Ждёт подтверждения</span>;
    }

    return <span className={styles.waiting}>Ждёт оплаты</span>;
  };

  const actionOf = (invoice: Invoice) => {
    if (invoice.paid_at !== null || invoice.reported_at !== null) return null;

    return (
      <button type="button" disabled={pendingId === invoice.id} onClick={() => void report(invoice.id)}>
        Я оплатил
      </button>
    );
  };

  const items = state.items.map((invoice) => ({
    key: String(invoice.id),
    title: `Счёт № ${invoice.number}`,
    meta: `Заявка №${invoice.expertise_id} · ${INVOICE_STAGE_LABELS[invoice.stage]} · ${formatRequestDate(invoice.created_at)}`,
    amount: formatRub(invoice.amount),
    href: invoicePdfUrl(invoice.id),
    status: statusOf(invoice),
    action: actionOf(invoice),
  }));

  return (
    <div className={styles.root}>
      {error && <p className={styles.error}>{error}</p>}
      <DocumentList items={items} />
    </div>
  );
};

export default InvoicesTab;
