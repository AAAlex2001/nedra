"use client";

import type { CommissionApplicationRecord } from "@/entities/commission";
import type { ExpertCatalog } from "@/entities/expert";
import Button from "@/shared/ui/button";
import { useCommissionApplications } from "../../model/use-commission-applications";
import ApplicationCard from "../application-card";
import styles from "./style.module.scss";

type ApplicationsListProps = {
  initialItems: CommissionApplicationRecord[];
  catalog: ExpertCatalog | null;
  basePath: string;
};

const ApplicationsList = ({ initialItems, catalog, basePath }: ApplicationsListProps) => {
  const { state, remove, refresh } = useCommissionApplications(initialItems, basePath);

  return (
    <div className={styles.root}>
      <div className={styles.toolbar}>
        <span className={styles.count}>Всего заявок: {state.items.length}</span>

        <Button onClick={() => void refresh()} loading={state.refreshing}>
          Обновить
        </Button>
      </div>

      {state.error && <p className={styles.error}>{state.error}</p>}

      {state.items.length === 0 ? (
        <p className={styles.empty}>Заявок пока нет.</p>
      ) : (
        <ul className={styles.list}>
          {state.items.map((item) => (
            <li key={item.id}>
              <ApplicationCard
                application={item}
                catalog={catalog}
                pending={state.pendingId === item.id}
                onDelete={(id) => void remove(id)}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ApplicationsList;
