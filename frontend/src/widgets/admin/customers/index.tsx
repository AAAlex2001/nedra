import type { CustomerRecord } from "@/entities/user";
import { formatDate } from "@/shared/lib/date";
import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type AdminCustomersProps = {
  items: CustomerRecord[];
  error: string | null;
};

const DAY = 24 * 60 * 60 * 1000;

const registeredSince = (items: CustomerRecord[], days: number) => {
  const edge = Date.now() - days * DAY;

  return items.filter((item) => new Date(item.created_at).getTime() >= edge).length;
};

const AdminCustomers = ({ items, error }: AdminCustomersProps) => {
  const withCompany = items.filter((item) => item.company_name).length;
  const withExpertise = items.filter((item) => item.expertises_count > 0).length;

  const stats = [
    { label: "Всего зарегистрировано", value: items.length },
    { label: "За последние 30 дней", value: registeredSince(items, 30) },
    { label: "За последние 7 дней", value: registeredSince(items, 7) },
    { label: "Заполнили реквизиты", value: withCompany },
    { label: "Подали хотя бы одну заявку", value: withExpertise },
  ];

  return (
    <section className={styles.section}>
      <div className={styles.heading}>
        <h1 className={styles.title}>Заказчики</h1>
        <AccentLine width={30} />
        <p className={styles.subtitle}>
          Все, кто зарегистрировался в «Блиц-эксперте» как заказчик: контакты, реквизиты
          организации и сколько заявок на экспертизу подано.
        </p>
      </div>

      {error ? (
        <p className={styles.error}>{error}</p>
      ) : (
        <>
          <dl className={styles.stats}>
            {stats.map((item) => (
              <div key={item.label} className={styles.stat}>
                <dt className={styles.statLabel}>{item.label}</dt>
                <dd className={styles.statValue}>{item.value}</dd>
              </div>
            ))}
          </dl>

          {items.length === 0 ? (
            <p className={styles.empty}>Пока никто не зарегистрировался.</p>
          ) : (
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
        </>
      )}
    </section>
  );
};

export default AdminCustomers;
