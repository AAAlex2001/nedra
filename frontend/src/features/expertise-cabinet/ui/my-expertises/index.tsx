"use client";

import { isFinished } from "@/entities/expertise";
import Button from "@/shared/ui/button";
import Loader from "@/shared/ui/loader";
import { useMyExpertises } from "../../model/use-my-expertises";
import ExpertiseCard from "../expertise-card";
import styles from "./style.module.scss";

type MyExpertisesProps = {
  kind: "active" | "finished";
};

const MyExpertises = ({ kind }: MyExpertisesProps) => {
  const { state, replace } = useMyExpertises();

  if (state.status === "loading") {
    return <Loader />;
  }

  if (state.status === "error") {
    return <p className={styles.error}>{state.message}</p>;
  }

  const items = state.items.filter((item) =>
    kind === "finished" ? isFinished(item) : !isFinished(item),
  );

  if (items.length === 0 && kind === "finished") {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyTitle}>Завершённых экспертиз пока нет</p>
        <p className={styles.emptyText}>
          Сюда переезжают заявки, по которым вы приняли работу. Заключение, счета и переписка
          с экспертом остаются доступны.
        </p>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyTitle}>Активных заявок нет</p>
        <p className={styles.emptyText}>
          Отправьте документацию на экспертизу: укажите объект, класс опасности и отрасль,
          приложите файлы. Эксперты по вашей области получат уведомление сразу.
        </p>
        <Button href="/blits-ekspert">Отправить документацию</Button>
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
          role="customer"
          onChange={replace}
        />
      ))}
    </div>
  );
};

export default MyExpertises;
