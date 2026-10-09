"use client";

import classNames from "classnames";
import type { Tariff } from "@/entities/tariff";
import Button from "@/shared/ui/button";
import { useAuditTariff } from "../../model/use-audit-tariff";
import styles from "../tariff-grid/style.module.scss";

type AuditTariffProps = {
  initialTariffs: Tariff[];
  basePath: string;
};

const AuditTariff = ({ initialTariffs, basePath }: AuditTariffProps) => {
  const { price, dirty, status, error, change, save } = useAuditTariff(initialTariffs, basePath);

  return (
    <div className={styles.root}>
      <div className={styles.toolbar}>
        <span className={styles.count}>{dirty ? "Есть несохранённые изменения" : "Изменений нет"}</span>

        <Button onClick={() => void save()} disabled={!dirty} loading={status === "saving"}>
          Сохранить
        </Button>
      </div>

      {status === "saved" && <p className={styles.saved}>Тариф сохранён.</p>}
      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.tableWrap}>
        <table className={classNames(styles.table, styles.tableNarrow)}>
          <thead>
            <tr>
              <th className={styles.headArea}>Услуга</th>
              <th className={styles.headObject}>Стоимость, ₽</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th className={styles.area}>
                <span className={styles.areaCode}>Аудит СУПБ</span>
                <span className={styles.areaTitle}>
                  Аудит системы управления промышленной безопасностью
                </span>
              </th>
              <td className={styles.cell}>
                <input
                  className={styles.input}
                  inputMode="numeric"
                  placeholder="—"
                  aria-label="Стоимость аудита СУПБ"
                  value={price}
                  onChange={(event) => change(event.target.value)}
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p className={styles.hint}>
        Цена в рублях без копеек, не менее 100 000 ₽. Пустое поле означает «по запросу».
      </p>
    </div>
  );
};

export default AuditTariff;
