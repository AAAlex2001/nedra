"use client";

import { useState } from "react";
import type { CustomerRecord } from "@/entities/user";
import { deleteCustomer } from "@/features/customers-admin";
import { formatDate } from "@/shared/lib/date";
import AccentLine from "@/shared/ui/accent-line";
import DeleteButton from "@/shared/ui/delete-button";
import styles from "./style.module.scss";

type AdminCustomersProps = {
  items: CustomerRecord[];
  error: string | null;
  basePath: string;
};

const AdminCustomers = ({ items, error, basePath }: AdminCustomersProps) => {
  const [deletedUserIds, setDeletedUserIds] = useState<number[]>([]);
  const customers = items.filter((customer) => !deletedUserIds.includes(customer.user_id));

  const removeCustomer = async (userId: number) => {
    await deleteCustomer(basePath, userId);
    setDeletedUserIds((current) => [...current, userId]);
  };

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

      {error && <p className={styles.error}>{error}</p>}

      {!error && customers.length === 0 && (
        <p className={styles.empty}>Пока никто не зарегистрировался.</p>
      )}

      {!error && customers.length > 0 && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Заказчик</th>
                <th>Контакты</th>
                <th>Организация</th>
                <th>Заявок</th>
                <th>Регистрация</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((item) => (
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
                  <td>
                    <DeleteButton
                      title="Удалить заказчика?"
                      description={`Аккаунт «${item.full_name}» (${item.email}) и доступ в личный кабинет будут удалены. Если у заказчика есть заявки или платежи, удалить его нельзя.`}
                      onConfirm={() => removeCustomer(item.user_id)}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
};

export default AdminCustomers;
