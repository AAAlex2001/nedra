"use client";

import Button from "@/shared/ui/button";
import Loader from "@/shared/ui/loader";
import { useMyExpertises } from "../../model/use-my-expertises";
import ExpertiseCard from "../expertise-card";
import styles from "./style.module.scss";

const MyExpertises = () => {
  const { state, replace } = useMyExpertises();

  if (state.status === "loading") {
    return <Loader />;
  }

  if (state.status === "error") {
    return <p className={styles.error}>{state.message}</p>;
  }

  if (state.items.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyTitle}>Заявок пока нет</p>
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
      {state.items.map((item) => (
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
