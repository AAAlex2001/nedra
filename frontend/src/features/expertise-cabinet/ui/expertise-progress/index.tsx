import { EXPERTISE_STEPS, stepIndex, type ExpertiseStatus } from "@/entities/expertise";
import styles from "./style.module.scss";

type ExpertiseProgressProps = {
  status: ExpertiseStatus;
};

const ExpertiseProgress = ({ status }: ExpertiseProgressProps) => {
  const current = stepIndex(status);

  return (
    <ol className={styles.steps} aria-label="Ход экспертизы">
      {EXPERTISE_STEPS.map((step, index) => {
        const done = index < current;
        const active = index === current;

        return (
          <li
            key={step.status}
            className={`${styles.step} ${done ? styles.done : ""} ${active ? styles.active : ""}`}
            aria-current={active ? "step" : undefined}
          >
            <span className={styles.dot} aria-hidden="true" />
            <span className={styles.label}>{step.label}</span>
          </li>
        );
      })}
    </ol>
  );
};

export default ExpertiseProgress;
