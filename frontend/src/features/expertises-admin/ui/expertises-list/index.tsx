"use client";

import type { ExpertCatalog } from "@/entities/expert";
import Button from "@/shared/ui/button";
import { Tabs } from "@/shared/ui/tabs";
import { useExpertises } from "../../model/use-expertises";
import type { ExpertiseAdminRecord, StatusFilter } from "../../model/types";
import ExpertiseCard from "../expertise-card";
import styles from "./style.module.scss";

type ExpertisesListProps = {
  initialItems: ExpertiseAdminRecord[];
  catalog: ExpertCatalog | null;
  basePath: string;
};

const FILTERS: { value: StatusFilter; label: string }[] = [
  { value: "waiting", label: "Ждут эксперта" },
  { value: "work", label: "В работе" },
  { value: "done", label: "Завершены" },
  { value: "all", label: "Все" },
];

const ExpertisesList = ({ initialItems, catalog, basePath }: ExpertisesListProps) => {
  const {
    visibleItems,
    filter,
    pendingId,
    refreshing,
    error,
    countFor,
    setFilter,
    save,
    remove,
    refresh,
  } = useExpertises(initialItems, basePath);

  const tabs = FILTERS.map((item) => ({
    key: item.value,
    label: `${item.label} · ${countFor(item.value)}`,
  }));

  const selectFilter = (key: string) => {
    const chosen = FILTERS.find((item) => item.value === key);

    if (chosen) setFilter(chosen.value);
  };

  return (
    <div className={styles.root}>
      <div className={styles.toolbar}>
        <Tabs items={tabs} active={filter} onSelect={selectFilter} label="Статус заявки" stretch />

        <Button loading={refreshing} onClick={() => void refresh()}>
          Обновить
        </Button>
      </div>

      {error && <p className={styles.error}>{error}</p>}

      {visibleItems.length === 0 ? (
        <p className={styles.empty}>Заявок нет.</p>
      ) : (
        <ul className={styles.list}>
          {visibleItems.map((item) => (
            <li key={item.id}>
              <ExpertiseCard
                expertise={item}
                catalog={catalog}
                pending={pendingId === item.id}
                onSave={(id, status, price) => void save(id, status, price)}
                onRemove={(id) => void remove(id)}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ExpertisesList;
