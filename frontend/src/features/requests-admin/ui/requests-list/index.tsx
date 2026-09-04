"use client";

import type { RequestRecord } from "@/entities/request";
import Button from "@/shared/ui/button";
import { useRequests } from "../../model/use-requests";
import RequestCard from "../request-card";
import styles from "./style.module.scss";

type RequestsListProps = {
  initialItems: RequestRecord[];
};

const RequestsList = ({ initialItems }: RequestsListProps) => {
  const { state, refresh } = useRequests(initialItems);

  return (
    <div className={styles.root}>
      <div className={styles.toolbar}>
        <span className={styles.count}>Всего заявок: {state.items.length}</span>

        <Button onClick={() => void refresh()} disabled={state.refreshing}>
          {state.refreshing ? "Обновляем…" : "Обновить"}
        </Button>
      </div>

      {state.error && <p className={styles.error}>{state.error}</p>}

      {state.items.length === 0 ? (
        <p className={styles.empty}>Заявок пока нет.</p>
      ) : (
        <ul className={styles.list}>
          {state.items.map((item) => (
            <li key={item.request_id}>
              <RequestCard request={item} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default RequestsList;
