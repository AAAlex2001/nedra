import type { CustomerRecord } from "@/entities/user";
import { formatDate } from "@/shared/lib/date";
import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type AdminCustomersProps = {
  items: CustomerRecord[];
  error: string | null;
};

const AdminCustomers = ({ items, error }: AdminCustomersProps) => (
  <section className={styles.section}>
    <div className={styles.heading}>
      <h1 className={styles.title}>Заказчики</h1>
      <AccentLine width={30} />
      <p className={styles.subtitle}>
        Все, кто зарегистрировался в «Блиц-эксперте» как заказчик: контакты, реквизиты
        организации и сколько заявок на экспертизу подано.
      </p>
    </div>

    {error && <p className={styles.error}>{error}</p>}

    {!error && items.length === 0 && (
      <p className={styles.empty}>Пока никто не зарегистрировался.</p>
    )}

    {!error && items.length > 0 && (
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Заказчик</th>
              <th>Контакты</th>
              <th>Организация</th>
              <th>Заявок</th>
              <th>Регистрация</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.user_id}>
                <td className={styles.name}>{item.full_name}</td>
                <td>
                  <a className={styles.link} href={`mailto:${item.email}`}>
                    {item.email}
                  </a>
                  <span className={styles.phone}>{item.phone}</span>
                </td>
                <td>
                  {item.company_name ? (
                    <>
                      <span className={styles.company}>{item.company_name}</span>
                      {item.company_inn && (
                        <span className={styles.inn}>ИНН {item.company_inn}</span>
                      )}
                    </>
                  ) : (
                    <span className={styles.muted}>не заполнены</span>
                  )}
                </td>
                <td className={styles.count}>{item.expertises_count}</td>
                <td className={styles.muted}>{formatDate(item.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )}
  </section>
);

export default AdminCustomers;
