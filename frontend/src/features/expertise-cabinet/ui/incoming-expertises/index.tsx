"use client";

import { objectLabel, type Certificate } from "@/entities/expert";
import Loader from "@/shared/ui/loader";
import { useIncomingExpertises } from "../../model/use-incoming-expertises";
import ExpertiseCard from "../expertise-card";
import FilterChips from "../filter-chips";
import styles from "./style.module.scss";

type IncomingExpertisesProps = {
  certificates: Certificate[];
};

const IncomingExpertises = ({ certificates }: IncomingExpertisesProps) => {
  const incoming = useIncomingExpertises(certificates);
  const { state } = incoming;

  if (state.status === "loading") {
    return <Loader />;
  }

  if (state.status === "error") {
    return <p className={styles.error}>{state.message}</p>;
  }

  const hasFilters = incoming.objectCodes.length > 1 || incoming.areaCodes.length > 1;

  return (
    <div className={styles.root}>
      {hasFilters && (
        <div className={styles.filters}>
          <FilterChips
            label="Объект"
            allLabel="Все объекты"
            options={incoming.objectCodes.map((code) => ({
              value: code,
              label: objectLabel(state.catalog, code),
            }))}
            value={incoming.objectCode}
            onSelect={incoming.setObjectCode}
          />
          <FilterChips
            label="Область"
            allLabel="Все области"
            options={incoming.areaCodes.map((code) => ({ value: code, label: code }))}
            value={incoming.areaCode}
            onSelect={incoming.setAreaCode}
          />
        </div>
      )}

      {incoming.visibleItems.length === 0 ? (
        <div className={styles.empty}>
          <p className={styles.emptyTitle}>Новых заявок нет</p>
          <p className={styles.emptyText}>
            Сюда попадают заявки по вашим областям аттестации, объектам и категории.
            О новой заявке сообщим уведомлением и письмом.
          </p>
        </div>
      ) : (
        <div className={styles.list}>
          {incoming.visibleItems.map((item) => (
            <ExpertiseCard
              key={item.id}
              expertise={item}
              catalog={state.catalog}
              role="expert"
              onChange={incoming.replace}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default IncomingExpertises;
