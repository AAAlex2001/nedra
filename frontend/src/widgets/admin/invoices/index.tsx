import type { Invoice } from "@/entities/billing";
import { InvoicesList } from "@/features/invoices-admin";
import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type AdminInvoicesProps = {
  items: Invoice[];
  error: string | null;
  basePath: string;
};

const AdminInvoices = ({ items, error, basePath }: AdminInvoicesProps) => (
  <section className={styles.section}>
    <div className={styles.heading}>
      <h1 className={styles.title}>Счета для юрлиц</h1>
      <AccentLine width={30} />
      <p className={styles.subtitle}>
        Счета, которые заказчики выставили себе сами. Когда деньги придут на расчётный счёт,
        отметьте оплату — заявка сразу перейдёт на следующий этап.
      </p>
    </div>

    {error ? (
      <p className={styles.error}>{error}</p>
    ) : (
      <InvoicesList initialItems={items} basePath={basePath} />
    )}
  </section>
);

export default AdminInvoices;
