"use client";

import type { RequestRecord } from "@/entities/request";
import { useRequests } from "../../model/use-requests";
import RequestCard from "../request-card";
import styles from "./style.module.scss";

type RequestsListProps = {
  initialItems: RequestRecord[];
};

const RequestsList = ({ initialItems }: RequestsListProps) => {
  const { state, remove, refresh } = useRequests(initialItems);

  return (
    <div className={styles.root}>
      <div className={styles.toolbar}>
        <span className={styles.count}>
          Всего заявок: {state.items.length}
        </span>

        <button
          type="button"
          className={styles.refresh}
          onClick={() => void refresh()}
          disabled={state.refreshing}
        >
          {state.refreshing ? "Обновляем…" : "Обновить"}
        </button>
      </div>

      {state.error && <p className={styles.error}>{state.error}</p>}

      {state.items.length === 0 ? (
        <p className={styles.empty}>Заявок пока нет.</p>
      ) : (
        <ul className={styles.list}>
          {state.items.map((item) => (
            <li key={item.request_id}>
              <RequestCard
                request={item}
                pending={state.pendingId === item.request_id}
                onDelete={(id) => void remove(id)}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default RequestsList;
