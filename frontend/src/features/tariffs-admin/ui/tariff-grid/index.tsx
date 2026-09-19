"use client";

import type { ExpertCatalog } from "@/entities/expert";
import { tariffKey, type Tariff } from "@/entities/tariff";
import Button from "@/shared/ui/button";
import { useTariffGrid } from "../../model/use-tariff-grid";
import styles from "./style.module.scss";

type TariffGridProps = {
  catalog: ExpertCatalog;
  initialTariffs: Tariff[];
  basePath: string;
};

const TariffGrid = ({ catalog, initialTariffs, basePath }: TariffGridProps) => {
  const { state, changeCell, save } = useTariffGrid(initialTariffs, catalog, basePath);

  return (
    <div className={styles.root}>
      <div className={styles.toolbar}>
        <span className={styles.count}>
          {state.dirty ? "Есть несохранённые изменения" : "Изменений нет"}
        </span>

        <Button onClick={() => void save()} disabled={!state.dirty} loading={state.status === "saving"}>
          Сохранить
        </Button>
      </div>

      {state.status === "saved" && <p className={styles.saved}>Тарифы сохранены.</p>}
      {state.error && <p className={styles.error}>{state.error}</p>}

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.headArea}>Область</th>
              {catalog.objects.map((item) => (
                <th key={item.code} className={styles.headObject} title={item.title}>
                  {item.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {catalog.areas.map((area) => (
              <tr key={area.code}>
                <th className={styles.area} title={area.title}>
                  <span className={styles.areaCode}>{area.code}</span>
                  <span className={styles.areaTitle}>{area.title}</span>
                </th>
                {catalog.objects.map((item) => {
                  const key = tariffKey(area.code, item.code);
                  const allowed = area.objects.includes(item.code);

                  return (
                    <td key={item.code} className={styles.cell}>
                      {allowed ? (
                        <input
                          className={styles.input}
                          inputMode="numeric"
                          placeholder="—"
                          aria-label={`${area.code}, ${item.label}`}
                          value={state.values[key] ?? ""}
                          onChange={(event) => changeCell(key, event.target.value)}
                        />
                      ) : (
                        <span className={styles.na}>н/д</span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className={styles.hint}>
        Цены в рублях без копеек. Пустая ячейка означает «по запросу». «н/д» — по этой
        области такой объект экспертизы не выдаётся.
      </p>
    </div>
  );
};

export default TariffGrid;
