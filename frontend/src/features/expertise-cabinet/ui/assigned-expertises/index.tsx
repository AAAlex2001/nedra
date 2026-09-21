"use client";

import type { Expertise } from "@/entities/expertise";
import Loader from "@/shared/ui/loader";
import { useAssignedExpertises } from "../../model/use-assigned-expertises";
import ExpertiseCard from "../expertise-card";
import styles from "./style.module.scss";

type AssignedExpertisesProps = {
  kind: "active" | "finished";
};

const EMPTY_TEXT = {
  active: {
    title: "В работе пока ничего нет",
    text: "Здесь появятся заявки, по которым вы нажали «Готов провести экспертизу»: договор, оплата, заключение и приёмка.",
  },
  finished: {
    title: "Завершённых экспертиз пока нет",
    text: "Сюда переезжают заявки, по которым заказчик принял работу. Документы и переписка остаются доступны.",
  },
};

const isFinished = (expertise: Expertise): boolean => expertise.status === "accepted";

const AssignedExpertises = ({ kind }: AssignedExpertisesProps) => {
  const { state, replace } = useAssignedExpertises();

  if (state.status === "loading") {
    return <Loader />;
  }

  if (state.status === "error") {
    return <p className={styles.error}>{state.message}</p>;
  }

  const items = state.items.filter((item) =>
    kind === "finished" ? isFinished(item) : !isFinished(item),
  );

  if (items.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyTitle}>{EMPTY_TEXT[kind].title}</p>
        <p className={styles.emptyText}>{EMPTY_TEXT[kind].text}</p>
      </div>
    );
  }

  return (
    <div className={styles.list}>
      {items.map((item) => (
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
