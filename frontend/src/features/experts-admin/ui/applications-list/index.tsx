"use client";

import type { ExpertApplicationRecord, ExpertCatalog } from "@/entities/expert";
import Button from "@/shared/ui/button";
import { Tabs } from "@/shared/ui/tabs";
import { useApplications } from "../../model/use-applications";
import type { StatusFilter } from "../../model/types";
import ApplicationCard from "../application-card";
import styles from "./style.module.scss";

type ApplicationsListProps = {
  initialItems: ExpertApplicationRecord[];
  catalog: ExpertCatalog | null;
  basePath: string;
};

const FILTERS: { value: StatusFilter; label: string }[] = [
  { value: "pending", label: "На проверке" },
  { value: "approved", label: "Одобрены" },
  { value: "rejected", label: "Отклонены" },
  { value: "all", label: "Все" },
];

const ApplicationsList = ({ initialItems, catalog, basePath }: ApplicationsListProps) => {
  const { state, visibleItems, setFilter, approve, reject, removeExpert, refresh } =
    useApplications(initialItems, basePath);

  const tabs = FILTERS.map((filter) => ({ key: filter.value, label: filter.label }));

  const selectFilter = (key: string) => {
    const chosen = FILTERS.find((filter) => filter.value === key);

    if (chosen) setFilter(chosen.value);
  };

  return (
    <div className={styles.root}>
      <div className={styles.toolbar}>
        <Tabs items={tabs} active={state.filter} onSelect={selectFilter} label="Статус заявки" />

        <Button onClick={() => void refresh()} loading={state.refreshing}>
          Обновить
        </Button>
      </div>

      {state.error && <p className={styles.error}>{state.error}</p>}

      {visibleItems.length === 0 ? (
        <p className={styles.empty}>Заявок нет.</p>
      ) : (
        <ul className={styles.list}>
          {visibleItems.map((item) => (
            <li key={item.id}>
              <ApplicationCard
                application={item}
                catalog={catalog}
                basePath={basePath}
                pending={state.pendingId === item.id}
                onApprove={(id) => void approve(id)}
                onReject={(id, comment) => void reject(id, comment)}
                onDeleteExpert={(application) => void removeExpert(application)}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ApplicationsList;
