"use client";

import { INVOICE_STAGE_LABELS, type Invoice } from "@/entities/billing";
import { formatRequestDate } from "@/entities/request";
import { formatRub } from "@/shared/lib/money";
import Button from "@/shared/ui/button";
import { useAdminInvoices } from "../../model/use-invoices";
import styles from "./style.module.scss";

type InvoicesListProps = {
  initialItems: Invoice[];
  basePath: string;
};

type InvoiceRowProps = {
  invoice: Invoice;
  pending: boolean;
  onConfirm: (id: number) => void;
};

const InvoiceRow = ({ invoice, pending, onConfirm }: InvoiceRowProps) => {
  const confirm = () => {
    if (window.confirm(`Отметить счёт № ${invoice.number} оплаченным?`)) {
      onConfirm(invoice.id);
    }
  };

  return (
    <article className={styles.card}>
      <div className={styles.head}>
        <span className={styles.number}>Счёт № {invoice.number}</span>
        <span className={invoice.paid_at ? styles.paid : styles.waiting}>
          {invoice.paid_at ? `Оплачен ${formatRequestDate(invoice.paid_at)}` : "Ждёт оплаты"}
        </span>
      </div>

      <p className={styles.meta}>
        Заявка №{invoice.expertise_id} · {INVOICE_STAGE_LABELS[invoice.stage]} ·{" "}
        {formatRequestDate(invoice.created_at)}
      </p>

      <p className={styles.payer}>
        {invoice.payer_name} · ИНН {invoice.payer_inn}
      </p>

      <div className={styles.foot}>
        <span className={styles.amount}>{formatRub(invoice.amount)}</span>

        {invoice.paid_at === null && (
          <Button loading={pending} onClick={confirm}>
            Деньги пришли
          </Button>
        )}
      </div>
    </article>
  );
};

const InvoicesList = ({ initialItems, basePath }: InvoicesListProps) => {
  const { items, pendingId, refreshing, error, confirm, refresh } = useAdminInvoices(
    initialItems,
    basePath,
  );

  return (
    <div className={styles.root}>
      <div className={styles.toolbar}>
        <span className={styles.count}>Всего счетов: {items.length}</span>
        <Button loading={refreshing} onClick={() => void refresh()}>
          Обновить
        </Button>
      </div>

      {error && <p className={styles.error}>{error}</p>}

      {items.length === 0 ? (
        <p className={styles.empty}>Счетов пока нет.</p>
      ) : (
        <div className={styles.list}>
          {items.map((item) => (
            <InvoiceRow
              key={item.id}
              invoice={item}
              pending={pendingId === item.id}
              onConfirm={(id) => void confirm(id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default InvoicesList;
