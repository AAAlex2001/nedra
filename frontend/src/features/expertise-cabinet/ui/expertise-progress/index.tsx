"use client";

import { useState } from "react";
import {
  buildStages,
  currentStage,
  doneCount,
  type Expertise,
  type ExpertiseStage,
} from "@/entities/expertise";
import { CheckIcon, ClockIcon } from "@/shared/ui/icons";
import Modal from "@/shared/ui/modal";
import styles from "./style.module.scss";

type ExpertiseProgressProps = {
  expertise: Expertise;
};

const formatDay = (value: string): string => {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
};

const periodText = (stage: ExpertiseStage): string => {
  if (stage.startedAt === null) return "";

  if (stage.endedAt !== null) {
    return `с ${formatDay(stage.startedAt)} по ${formatDay(stage.endedAt)}`;
  }

  if (stage.state === "done") return formatDay(stage.startedAt);

  return `с ${formatDay(stage.startedAt)}`;
};

const StageMarker = ({ state }: { state: ExpertiseStage["state"] }) => (
  <span className={styles.marker} aria-hidden="true">
    {state === "done" && <CheckIcon className={styles.markerIcon} />}
    {state === "current" && <ClockIcon className={styles.markerIcon} />}
    {state === "future" && <span className={styles.markerFuture} />}
  </span>
);

const ExpertiseProgress = ({ expertise }: ExpertiseProgressProps) => {
  const [open, setOpen] = useState(false);

  const stages = buildStages(expertise);
  const current = currentStage(stages);
  const passed = doneCount(stages);

  return (
    <>
      <button type="button" className={styles.summary} onClick={() => setOpen(true)}>
        <span className={styles.head}>
          <span className={styles.status}>{current ? current.label : "Заявка подана"}</span>
          <span className={styles.counter}>
            шаг {passed} из {stages.length}
          </span>
        </span>

        <span className={styles.bar} aria-hidden="true">
          {stages.map((stage) => (
            <span key={stage.key} className={`${styles.segment} ${styles[stage.state]}`} />
          ))}
        </span>

        <span className={styles.foot}>
          {current && current.startedAt !== null && (
            <span className={styles.since}>в статусе с {formatDay(current.startedAt)}</span>
          )}
          <span className={styles.more}>вся история</span>
        </span>
      </button>

      <Modal open={open} title="История статусов" onClose={() => setOpen(false)}>
        <ol className={styles.history}>
          {stages.map((stage) => (
            <li key={stage.key} className={`${styles.row} ${styles[stage.state]}`}>
              <StageMarker state={stage.state} />

              <span className={styles.text}>
                <span className={styles.label}>{stage.label}</span>
                {periodText(stage) !== "" && (
                  <span className={styles.period}>{periodText(stage)}</span>
                )}
              </span>
            </li>
          ))}
        </ol>
      </Modal>
    </>
  );
};

export default ExpertiseProgress;
