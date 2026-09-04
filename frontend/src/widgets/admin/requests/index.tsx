import type { RequestRecord } from "@/entities/request";
import { RequestsList } from "@/features/requests-admin";
import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type AdminRequestsProps = {
  items: RequestRecord[];
  error: string | null;
};

const AdminRequests = ({ items, error }: AdminRequestsProps) => {
  return (
    <section className={styles.section}>
      <div className={styles.heading}>
        <h1 className={styles.title}>Заявки с сайта</h1>
        <AccentLine width={30} />
        <p className={styles.subtitle}>
          Список заявок, оставленных через форму на главной странице.
        </p>
      </div>

      {error ? (
        <p className={styles.error}>{error}</p>
      ) : (
        <RequestsList initialItems={items} />
      )}
    </section>
  );
};

export default AdminRequests;
