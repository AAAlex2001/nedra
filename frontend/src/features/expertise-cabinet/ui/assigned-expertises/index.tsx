"use client";

import Loader from "@/shared/ui/loader";
import type { useAssignedExpertises } from "../../model/use-assigned-expertises";
import ExpertiseCard from "../expertise-card";
import styles from "./style.module.scss";

type AssignedExpertisesProps = {
  assigned: ReturnType<typeof useAssignedExpertises>;
};

const AssignedExpertises = ({ assigned }: AssignedExpertisesProps) => {
  const { state, replace } = assigned;

  if (state.status === "loading") {
    return <Loader />;
  }

  if (state.status === "error") {
    return <p className={styles.error}>{state.message}</p>;
  }

  if (state.items.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyTitle}>В работе пока ничего нет</p>
        <p className={styles.emptyText}>
          Здесь появятся заявки, по которым вы нажали «Готов провести экспертизу»: договор,
          оплата, заключение и приёмка.
        </p>
      </div>
    );
  }

  return (
    <div className={styles.list}>
      {state.items.map((item) => (
        <ExpertiseCard
          key={item.id}
          expertise={item}
          catalog={state.catalog}
          role="expert"
          onChange={replace}
        />
      ))}
    </div>
  );
};

export default AssignedExpertises;
