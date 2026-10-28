"use client";

import classNames from "classnames";
import { useState } from "react";
import { CheckIcon } from "@/shared/ui/icons";
import Modal from "@/shared/ui/modal";
import type { Steps } from "../../model/use-steps";
import styles from "./style.module.scss";

type OrderStepsProps = {
  steps: Steps;
};

type StepState = "done" | "current" | "future";

const stateOf = (position: number, current: number): StepState => {
  if (position < current) return "done";
  if (position === current) return "current";
  return "future";
};

const StepMarker = ({ state }: { state: StepState }) => (
  <span className={styles.marker} aria-hidden="true">
    {state === "done" ? <CheckIcon className={styles.markerIcon} /> : <span className={styles.dot} />}
  </span>
);

const OrderSteps = ({ steps }: OrderStepsProps) => {
  const [open, setOpen] = useState(false);

  return (
    <div className={styles.summary}>
      <div className={styles.head}>
        <span className={styles.status}>
          Шаг {steps.index + 1} из {steps.list.length} · {steps.current.title}
        </span>
        <button type="button" className={styles.more} onClick={() => setOpen(true)}>
          Все шаги
        </button>
      </div>

      <span className={styles.bar} aria-hidden="true">
        {steps.list.map((step, position) => (
          <span
            key={step.key}
            className={classNames(styles.segment, styles[stateOf(position, steps.index)])}
          />
        ))}
      </span>

      {steps.upcoming && <span className={styles.upcoming}>Далее: {steps.upcoming.title}</span>}

      <Modal open={open} title="Шаги заявки" onClose={() => setOpen(false)}>
        <ol className={styles.list}>
          {steps.list.map((step, position) => {
            const state = stateOf(position, steps.index);

            return (
              <li key={step.key} className={classNames(styles.row, styles[state])}>
                <StepMarker state={state} />
                <span className={styles.label}>{step.title}</span>
              </li>
            );
          })}
        </ol>
      </Modal>
    </div>
  );
};

export default OrderSteps;
