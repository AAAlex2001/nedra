"use client";

import type { Certificate } from "@/entities/expert";
import { objectLabel } from "@/entities/expert";
import Chip from "@/shared/ui/chip";
import Loader from "@/shared/ui/loader";
import type { useIncomingExpertises } from "../../model/use-incoming-expertises";
import ExpertiseCard from "../expertise-card";
import styles from "./style.module.scss";

type IncomingExpertisesProps = {
  certificates: Certificate[];
  incoming: ReturnType<typeof useIncomingExpertises>;
};

const unique = (values: string[]): string[] => {
  const seen: string[] = [];
  for (const value of values) {
    if (!seen.includes(value)) seen.push(value);
  }
  return seen;
};

const IncomingExpertises = ({ certificates, incoming }: IncomingExpertisesProps) => {
  const { state, visibleItems, objectCode, areaCode, setObjectCode, setAreaCode, replace } =
    incoming;

  const objectCodes = unique(certificates.map((item) => item.object_code));
  const areaCodes = unique(certificates.map((item) => item.area_code));
  const showFilters = state.status === "ready" && (objectCodes.length > 1 || areaCodes.length > 1);

  return (
    <div className={styles.root}>
      {showFilters && state.status === "ready" && (
        <div className={styles.filters}>
          {objectCodes.length > 1 && (
            <div className={styles.chips} role="group" aria-label="Объект">
              <Chip active={objectCode === ""} onClick={() => setObjectCode("")}>
                Все объекты
              </Chip>
              {objectCodes.map((code) => (
                <Chip key={code} active={objectCode === code} onClick={() => setObjectCode(code)}>
                  {objectLabel(state.catalog, code)}
                </Chip>
              ))}
            </div>
          )}

          {areaCodes.length > 1 && (
            <div className={styles.chips} role="group" aria-label="Область">
              <Chip active={areaCode === ""} onClick={() => setAreaCode("")}>
                Все области
              </Chip>
              {areaCodes.map((code) => (
                <Chip key={code} active={areaCode === code} onClick={() => setAreaCode(code)}>
                  {code}
                </Chip>
              ))}
            </div>
          )}
        </div>
      )}

      {state.status === "loading" && <Loader />}
      {state.status === "error" && <p className={styles.error}>{state.message}</p>}

      {state.status === "ready" && visibleItems.length === 0 && (
        <div className={styles.empty}>
          <p className={styles.emptyTitle}>Новых заявок нет</p>
          <p className={styles.emptyText}>
            Сюда попадают заявки по вашим областям аттестации, объектам и категории.
            О новой заявке сообщим уведомлением и письмом.
          </p>
        </div>
      )}

      {state.status === "ready" && visibleItems.length > 0 && (
        <div className={styles.list}>
          {visibleItems.map((item) => (
            <ExpertiseCard
              key={item.id}
              expertise={item}
              catalog={state.catalog}
              role="expert"
              onChange={replace}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default IncomingExpertises;
